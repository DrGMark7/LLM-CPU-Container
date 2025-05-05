#!/usr/bin/env python3
import os
import sys
import time
import random
import logging
import grpc
import json

# Add the parent directory to the path so we can import the generated modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the generated gRPC code
import llm
import proto.worker_pb2
import proto.worker_pb2_grpc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WorkerClient:
    """Client for the gRPC worker service that polls for jobs and processes them."""
    
    def __init__(self, server_address=None):
        """Initialize the worker client with the server address."""
        # Use environment variable for server address, fallback to parameter or default
        self.server_address = server_address or os.environ.get('GRPC_SERVER', 'localhost:50051')
        
        # Get polling interval from environment variable (in milliseconds)
        try:
            self.polling_interval = float(os.environ.get('POLLING_INTERVAL_MS', '5000')) / 1000.0
        except ValueError:
            logger.warning("Invalid POLLING_INTERVAL_MS value, using default 5000ms")
            self.polling_interval = 5.0
            
        self.channel = None
        self.stub = None
        self.should_run = True
        self.connect()
        
    def connect(self):
        """Connect to the gRPC server."""
        self.channel = grpc.insecure_channel(self.server_address)
        self.stub = proto.worker_pb2_grpc.WorkerServiceStub(self.channel)
    
    def close(self):
        """Close the gRPC channel."""
        if self.channel:
            self.channel.close()
            self.channel = None
            self.stub = None
    
    def request_job(self):
        """Request a job from the server."""
        try:
            logger.info("Requesting job from server")
            response = self.stub.RequestJob(proto.worker_pb2.JobRequest())
            return response
        except grpc.RpcError as e:
            logger.error(f"RPC error while requesting job: {e.code()}: {e.details()}")
            # Reconnect if there was a connection issue
            if e.code() in [grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.DEADLINE_EXCEEDED]:
                logger.info("Reconnecting to server")
                self.close()
                time.sleep(2)  # Wait before reconnecting
                self.connect()
            return None
    
    def complete_job(self, job_id, result_payload):
        """Report job completion to the server."""
        try:
            logger.info(f"Completing job {job_id}")
            result = proto.worker_pb2.JobResult(job_id=job_id, payload=result_payload)
            response = self.stub.CompleteJob(result)
            return response.success
        except grpc.RpcError as e:
            logger.error(f"RPC error while completing job: {e.code()}: {e.details()}")
            return False
    
    def process_job(self, job):
        """Process a job and return the result."""
        logger.info(f"Processing job {job.id} with payload: {job.payload}")

        llm_response = llm.get_response(job.payload)
        
        result = json.dumps(llm_response)
        
        logger.info(f"Job {job.id} processed.")
        
        return result
    
    def run(self):
        """Main worker loop: continuously poll for jobs and process them."""
        logger.info("Starting worker loop")
        
        while self.should_run:
            try:
                # Request a job from the server
                job = self.request_job()
                
                # If we received a job with an ID, process it
                if job and job.id:
                    logger.info(f"Received job {job.id}")
                    
                    # Process the job
                    result = self.process_job(job)
                    
                    # Report the job completion
                    success = self.complete_job(job.id, result)
                    
                    if success:
                        logger.info(f"Job {job.id} completed successfully")
                    else:
                        logger.warning(f"Failed to report completion for job {job.id}")
                
                # If no job is available, wait before polling again
                else:
                    logger.debug("No job available, waiting before polling again")
                    time.sleep(self.polling_interval)  # Wait according to polling interval
            
            except Exception as e:
                logger.error(f"Error in worker loop: {str(e)}")
                time.sleep(self.polling_interval)  # Wait before retrying
    
    def stop(self):
        """Stop the worker loop and clean up."""
        logger.info("Stopping worker")
        self.should_run = False
        self.close()

