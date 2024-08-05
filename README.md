# Theatre API Service

## Description

The Theatre API Service is a RESTful API designed to manage and facilitate interactions with theatre-related data, including plays, performances, actors, genres, and reservations. This service allows users to easily access and manipulate theatre data through a structured and secure interface.

---

## Features
- **Manage Plays**: Create, read, update, and delete plays, including details like title, description, and associated genres and actors.
- **Performance Scheduling**: Schedule performances with specific showtimes and link them to theatre halls.
- **Actor Management**: Maintain a database of actors, including their names and associated plays.
- **Genre Classification**: Categorize plays into various genres for easier navigation and filtering.
- **Reservation System**: Allow users to reserve tickets for performances and manage their reservations.
- **Ticketing**: Handle ticket creation and validation for specific performances.

---

## Installing / Getting started

To get the Task Manager up and running, follow these steps:

1. **Install Docker**:
https://www.docker.com/

2. **Clone the Repository**:
    ```bash
    git clone https://github.com/frontbastard/pf-theatre-api-service
    cd pf-theatre-api-service/
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up Environment Variables**:
    Rename the `.env.example` file to `.env` in the root directory and add the necessary environment variables.

5. **Run the Project**:
    ```bash
    docker-compose up --build
    ```

### What this command will do:
- Create the theater, db, test containers
- Make migrations
- Create a superuser with the credentials described in the `.env` file
- Fill the database with test data
- Make the API available at [localhost:8001](http://localhost:8001)

---

## Swagger
After launching the project, swagger will be available at http://localhost:8001/api/v1/doc/swagger/

---

## Testing
To execute the tests, you need to add permissions to the `run_tests.sh` file and run this file:
```bash
chmod +x run_tests.sh
./run_tests.sh
```

---

## Contributing

We welcome contributions to the Task Manager project. To contribute, please fork the repository and create a feature branch. Pull requests are warmly welcome.

---

## Links

- **Repository:** [GitHub Repository](https://github.com/frontbastard/pf-theatre-api-service/)
- **Issue Tracker:** [GitHub Issues](https://github.com/frontbastard/pf-theatre-api-service/issues)

---

**Licensing**

The code in this project is licensed under the MIT License.
