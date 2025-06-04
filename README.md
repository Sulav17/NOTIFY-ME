 # NotifyMe
 
 NotifyMe is a simple notification microservice built with FastAPI that lets other applications enqueue notifications (like emails or SMS) in the background. It stores notification requests in a MySQL database, pushes them into a RabbitMQ queue for processing, rate-limits requests via Redis, and logs events into an ELK stack for monitoring.
 
 ## 🚀 Purpose and Use Case
 
 - **Decouple** your main application from slow or unreliable tasks (e.g., sending emails/SMS).
 - **Queue** notifications so they can be retried or processed later without holding up HTTP requests.
 - **Rate-limit** by recipient to prevent spamming.
 - **Monitor** all notification events with ELK (Elasticsearch, Logstash, Kibana).
 
 Imagine you run a digital wallet app. Whenever a user pays, you need to send them a confirmation SMS or email. Instead of making the user wait while your server talks to an SMS gateway or email API, you post a notification job to NotifyMe and immediately return a response. NotifyMe takes care of the rest in the background.
 
 ## 📦 Technology Stack
 
 - **FastAPI**: HTTP API for accepting notification requests.
 - **Uvicorn**: ASGI server to run FastAPI.
 - **SQLAlchemy + MySQL**: store notification records and their status.
 - **Redis**: in-memory cache for rate limiting per recipient.
 - **RabbitMQ**: reliable queue for background processing.
 - **aio-pika**: async RabbitMQ client.
 - **ELK Stack**: collects and visualizes logs.
   - **Logstash**: ingests logs via Beats or TCP.
   - **Elasticsearch**: indexes log data.
   - **Kibana**: dashboard for searching logs.
 - **Docker & Docker Compose**: containerize and orchestrate all services.
 - **Pydantic**: data validation and settings management.
 - **pytest**: unit tests for core components.
 
 ## 📐 Architecture Overview
 
 ```
 client app  -->  NotifyMe API  -->  MySQL (store)
                                  |
                                  +--> Redis (rate limit)
                                  |
                                  +--> RabbitMQ queue  -->  NotifyMe consumer  -->  update MySQL status
                                                                   |
                                                                   +--> call external email/SMS gateway
                                                                  
  NotifyMe (FastAPI) also logs all events to Logstash --> Elasticsearch --> Kibana
 ```
 
 ### Component Details
 
 - **API Server** (`app/main.py`):
   - Runs on Uvicorn (0.0.0.0:8000).
   - On startup:
     1. Waits for MySQL, creates tables.
     2. Launches a background task (consumer) to process the RabbitMQ queue.
 - **Router** (`app/api/v1/notify.py`):
   - Single `POST /api/v1/notify/` endpoint.
   - Validates payload (`recipient`, `message`).
   - Checks Redis-based rate limiter.
   - Saves a notification record in MySQL.
   - Publishes the record ID to RabbitMQ for async processing.
 - **Rate Limiter** (`app/services/rate_limiter.py`):
   - Uses Redis to count requests per recipient over a time window.
 - **RabbitMQ Producer** (`app/services/rabbitmq.py`):
   - Async function to publish JSON messages to the `notification_queue`.
 - **Consumer** (`app/tasks/consumer.py`):
   - Async task started alongside the API.
   - Connects to RabbitMQ (retries until ready).
   - Consumes messages, updates the corresponding MySQL record status to `sent`.
   - (You can extend it to actually send emails/SMS via external APIs.)
 - **Logging**:
   - The application logs to stdout in JSON format.
   - Docker Compose routes these logs into Logstash on port 5044.
   - Logstash ships them into Elasticsearch for indexing.
   - Use Kibana (localhost:5601) to explore logs.
 
 ## 🎯 Getting Started
 
 ### Prerequisites
 - Docker & Docker Compose installed.
 
 ### Run the stack
 ```bash
 git clone <repo-url>
 cd notifyme
 docker-compose up --build -d
 ```
 - The API will be available at http://localhost:8000.
 - Swagger docs: http://localhost:8000/docs
 - Kibana dashboard: http://localhost:5601
 
 ### Send a Test Notification
 ```bash
 curl -X POST http://localhost:8000/api/v1/notify/ \
   -H "Content-Type: application/json" \
   -d '{ "recipient": "+9779800000000", "message": "Hello from NotifyMe!" }'
 ```
 
 ## 🔄 Integration in Large-Scale Projects
 
 1. **Email/SMS Services**: Extend the consumer:
    - After marking status=`sent`, call an email API (e.g., SMTP, SendGrid) or SMS gateway.
    - You can route messages to different queues (e.g., `email_queue`, `sms_queue`) and have dedicated consumers.
 2. **Scalability**:
    - Run multiple API replicas behind a load balancer.
    - Scale RabbitMQ consumers horizontally for high throughput.
    - Use managed services (AWS RDS, ElastiCache, Amazon MQ) for reliability.
 3. **Monitoring & Alerting**:
    - Kibana + Elasticsearch for real-time log search and dashboards.
    - Set up alerts on error rates or queue backlogs.
 4. **Resilience**:
    - Dead-letter queue for failed notifications.
    - Database migrations via Alembic for schema changes.
 
 ## 🎓 How It All Connects
 
 1. **Startup**: Docker Compose launches MySQL, Redis, RabbitMQ, ELK, and the NotifyMe app.
 2. **API Ready**: NotifyMe waits for MySQL, creates tables, then starts the HTTP server and the RabbitMQ consumer task.
 3. **Incoming Request**: Client calls `POST /api/v1/notify/` with recipient + message.
 4. **Rate Limiting**: FastAPI checks Redis to ensure the recipient hasn’t been spammed.
 5. **Database**: A new record is inserted in MySQL (`pending` status).
 6. **Queue**: API publishes the notification ID to the RabbitMQ `notification_queue`.
 7. **Consumer**: Background task reads from the queue, updates the MySQL record status to `sent`.
 8. **External Delivery**: (Future) consumer calls SMS/email APIs to deliver the message.
 9. **Logging Pipeline**: All steps log JSON messages; Logstash → Elasticsearch → Kibana surfaces metrics and errors.
 
 With this setup, your main application never waits for slow network calls, and you gain full control over retry logic, scaling, and observability. Perfect for any high-traffic system—whether you’re sending wallet alerts in Nepal or mass email campaigns!
 
 ## 🤔 Why is status "pending"?

 When you send a notification via `POST /api/v1/notify/`, the API immediately:
 1. Inserts a record in MySQL with status `pending`.
 2. Publishes the record ID to the RabbitMQ queue for asynchronous processing.

 The background consumer fetches the message from RabbitMQ and updates the record status to `sent`. Depending on system load and retry timing, it can take a few seconds for the status to change.

 ## 🔍 Inspecting the Database

 To verify that notifications are stored and see their status:
 ```bash
 # Open a MySQL shell in the running container
 docker-compose exec mysql mysql -u root -p12345ABc -D notifyme

 # In the MySQL prompt:
 SELECT id, recipient, message, status FROM notifications;
 ```
 Or run a single command:
 ```bash
 docker-compose exec mysql mysql -u root -p12345ABc -D notifyme \
   -e "SELECT id, recipient, message, status, created_at FROM notifications;"
 ```

 ## 🌍 Exposing & Consuming as an Open Source Project

 To enable external developers to use your NotifyMe service:
 1. **Publish the repository** on GitHub/GitLab and add a `LICENSE` (e.g., MIT).
 2. **Provide a `.env.example`** listing required variables (`MYSQL_*`, `REDIS_*`, `RABBITMQ_URL`, etc.).
 3. **Leverage Swagger/OpenAPI**: clients can auto-generate SDKs from the spec at `/openapi.json`.
 4. **Distribute Docker images**: build & push to Docker Hub (`yourname/notifyme:latest`) so users can `docker pull`.
 5. **Document usage examples** in popular languages (Python, JavaScript, etc.) showing how to `POST` notifications.
 6. **Configure CORS and security** in `app/main.py` if you intend to serve browser-based clients or enforce API keys.

 By following these steps, others can clone, configure, and deploy NotifyMe in their own environments, integrating it seamlessly into their applications.
 
 ## 📜 License

 This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

 ## 🤝 Contributing

 Contributions are welcome! Please fork the repository at [github.com/Sulav17/notifyme](https://github.com/Sulav17/notifyme), make your changes, and open a pull request. If you encounter bugs or have feature requests, create an issue via the [issue tracker](https://github.com/Sulav17/notifyme/issues).

 ## 🔔 Usage Notifications

 If you’re using NotifyMe in your project, please give the repo a star ⭐ on GitHub. It helps me see who’s using it and prioritize community feedback!