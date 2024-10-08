import docker
import tempfile
import os
import uuid
import time

# Create a Docker client instance
docker_client = docker.from_env()

def start_container(code_and_test: str):
    try:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate a unique filename
            unique_filename = f"code_{uuid.uuid4().hex}.py"
            file_path = os.path.join(temp_dir, unique_filename)

            # Write the code and test to a single file
            with open(file_path, "w") as file:
                file.write(code_and_test)

            # Create a Dockerfile to use Python and run pytest
            dockerfile_content = f"""
            FROM python:3.11
            WORKDIR /app
            COPY {unique_filename} /app/{unique_filename}
            RUN pip install pytest
            CMD ["pytest", "/app/{unique_filename}", "-v", "-k", "test_"]
            """

            dockerfile_path = os.path.join(temp_dir, "Dockerfile")
            
            with open(dockerfile_path, "w") as dockerfile:
                dockerfile.write(dockerfile_content)

            # Build the Docker image
            build_start_time = time.time()
            image, build_logs = docker_client.images.build(path=temp_dir, tag="generated_test_image")
            build_end_time = time.time()
            build_elapsed_time = (build_end_time - build_start_time) * 1000  # Convert to milliseconds
            print(f"Image build time: {build_elapsed_time:.2f} ms")
            # for log in build_logs:
            #     print(log.get('stream', ''))

            # Measure the time taken to run the Docker container and capture the output
            container_start_time = time.time()

            # Run the Docker container and capture the output
            container = docker_client.containers.run(image="generated_test_image", detach=True)
            container_logs = container.logs(stream=True)

            container_end_time = time.time()
            container_elapsed_time = (container_end_time - container_start_time) * 1000  # Convert to milliseconds

            print(f"Container run time: {container_elapsed_time:.2f} ms")

            # Retrieve the log output as the container runs
            result_logs = ""
            for log in container_logs:
                result_logs += log.decode('utf-8')

            # Wait for the container to finish and remove it
            container.wait()
            container.remove()

            # Remove the Docker image
            docker_client.images.remove(image.id, force=True)

            return result_logs
    except Exception as e:
        return {"error": str(e)}

# Example usage
code_and_test = """
def add(a, b):
    return a + b

def test_add():
    assert add(1, 2) == 3
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
"""

start_time = time.time()

result = start_container(code_and_test)

end_time = time.time()
elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds

print(result)
print(f"Elapsed time: {elapsed_time:.2f} ms")