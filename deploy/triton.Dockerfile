FROM nvcr.io/nvidia/tritonserver:24.12-py3
COPY models /models
CMD ["tritonserver", "--model-repository=/models", "--http-port=8990", "--grpc-port=8991", "--metrics-port=8992"]
