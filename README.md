# Microservices Tracing with Kong, OpenTelemetry, and Honeycomb

This project demonstrates a microservices architecture using Kong as an API gateway, OpenTelemetry for distributed tracing, and Honeycomb.io for observability. It consists of multiple services orchestrated with Docker Compose.

## Project Components

- **Kong**: API Gateway
- **OpenTelemetry Collector**: Collects and exports tracing data
- **Service1**: A sample microservice
- **Service2**: Another sample microservice
- **Client**: A service that continuously calls Service1 and Service2 through Kong

## Prerequisites

- Docker and Docker Compose
- A Honeycomb.io account and API key

## Setup

1. Clone this repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create a `.env` file in the root directory with your Honeycomb.io credentials:
   ```
   HONEYCOMB_API_KEY=your_api_key_here
   HONEYCOMB_DATASET=your_dataset_name
   ```

3. Create the external Docker network:
   ```
   docker network create kong-net
   ```

## Running the Project

1. Start the OpenTelemetry Collector:
   ```
   docker-compose -f docker-compose-collector.yml up -d
   ```

2. Start the main application:
   ```
   docker-compose up --build
   ```

3. The client service will automatically start making requests to Service1 and Service2 through Kong.

## Project Structure

```
.
├── docker-compose.yml
├── docker-compose-collector.yml
├── kong
│   └── kong.yml
├── otel-collector
│   └── otel-collector-config.yml
├── service1
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── service2
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
└── client
    ├── Dockerfile
    ├── requirements.txt
    └── app.py
```

## Monitoring

Once the application is running, you can view the traces in your Honeycomb.io dashboard.

## Troubleshooting

- If services fail to start, check the logs:
  ```
  docker-compose logs <service-name>
  ```
- Ensure all required ports are free on your host machine.
- Verify that the `kong-net` network exists and all services are connected to it.

## Extending the Project

To add new services:
1. Create a new directory for your service.
2. Add the service to the `docker-compose.yml` file.
3. Update Kong configuration in `kong/kong.yml` to route traffic to your new service.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
