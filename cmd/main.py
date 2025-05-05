import os
import sys
import logging

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from worker_service.service import WorkerClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the worker client."""
    try:
        # Get server address from environment variable
        server_address = os.environ.get('GRPC_SERVER')
        
        # Log server info
        if server_address:
            logger.info(f"Using server address from environment: {server_address}")
        else:
            logger.info("Using default server address: localhost:50051")
        
        # Create and run the worker client
        worker = WorkerClient(server_address)
        
        # Run the worker loop
        worker.run()
    
    except KeyboardInterrupt:
        logger.info("Worker interrupted by user")
    
    except Exception as e:
        logger.error(f"Worker failed with error: {str(e)}")
        sys.exit(1)
    
    finally:
        # Ensure clean shutdown
        if 'worker' in locals():
            worker.stop()

if __name__ == "__main__":
    main()