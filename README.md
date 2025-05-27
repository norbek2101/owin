# Owin - Commercial Proposal Editor

Owin is a web-based application designed to streamline the creation and management of commercial proposals for clients. Built with Django and Django REST Framework, Owin provides a robust API for user authentication and proposal management, integrated with a custom user model and a user-friendly admin interface. The application supports client and proposal CRUD operations, secure JWT-based authentication, and data isolation for user-specific records.

## Features

- **Custom User Authentication**:
  - User registration and login via email or phone number.
  - JWT-based authentication using `djangorestframework-simplejwt`.
  - Custom user model with `name`, `email`, `phone_number`, and permission fields.
- **Client Management**:
  - Create, list, retrieve, update, and delete clients with fields for `company_name`, `address`, `phone_number`, `email`, and `added_by`.
  - User-specific access: users can only manage their own clients.
- **Proposal Management**:
  - Create, list, retrieve, update, and delete proposals linked to clients, with `title`, `description`, and `created_by` fields.
  - User-specific access: users can only manage their own proposals.
- **Admin Interface**:
  - Django admin with customized views for `User`, `Client`, and `Proposal` models.
  - Features autocomplete fields, search, filtering, and optimized querysets.
- **Testing**:
  - Comprehensive test suite using `pytest-django`, covering authentication, client, and proposal APIs (47 tests, 100% passing).
- **Security**:
  - JWT authentication for all API endpoints.
  - User-specific data isolation (`added_by`/`created_by` restrictions).
  - Validation for required fields (e.g., `phone_number` or `email` for clients).

## Project Structure

```
owin/
├── accounts/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── auth_backend.py
│   ├── managers.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── proposals/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── pytest.ini
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.13.2
- Django 5.2.1
- Django REST Framework
- `djangorestframework-simplejwt`
- `phonenumber-field`
- `pytest-django` (for testing)

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/yourusername/owin.git
   cd owin
   ```

2. **Set Up Virtual Environment**:

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Apply Migrations**:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a Superuser**:

   ```bash
   python manage.py createsuperuser
   ```

6. **Run the Development Server**:

   ```bash
   python manage.py runserver
   ```

   Access the app at `http://localhost:8000/` and the admin interface at `http://localhost:8000/admin/`.

## Configuration

Update `config/settings.py` for production use:

- Set `DEBUG = False`.
- Configure `DATABASES` for PostgreSQL or another production database.
- Secure `SECRET_KEY` using environment variables (e.g., with `python-decouple`).
- Enable HTTPS with `SECURE_SSL_REDIRECT = True`.
- Configure `SIMPLE_JWT` settings (e.g., token lifetimes).

Example `.env` file:

```
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=postgres://user:password@localhost:5432/owin
```

## API Endpoints

All API endpoints require JWT authentication. Obtain a token via the `/auth/login/` endpoint.

### Authentication (`/auth/`)

- **POST /auth/register/**: Register a new user.

  ```json
  {
      "name": "John Doe",
      "email": "john@example.com",
      "password": "secure123"
  }
  ```

- **POST /auth/login/**: Log in and obtain JWT tokens.

  ```json
  {
      "identifier": "john@example.com",
      "password": "secure123"
  }
  ```

- **POST /auth/logout/**: Log out (blacklist refresh token).

- **GET /auth/profile/**: Retrieve authenticated user’s profile.

### Clients (`/api/clients/`)

- **GET /api/clients/**: List clients (user-specific).

- **POST /api/clients/**: Create a client.

  ```json
  {
      "company_name": "Acme Corp",
      "email": "contact@acme.com",
      "phone_number": "+12025550123"
  }
  ```

- **GET /api/clients//**: Retrieve a client.

- **PUT/PATCH /api/clients//**: Update a client.

- **DELETE /api/clients//**: Delete a client.

### Proposals (`/api/proposals/`)

- **GET /api/proposals/**: List proposals (user-specific).

- **POST /api/proposals/**: Create a proposal.

  ```json
  {
      "client_id": 1,
      "title": "Website Redesign",
      "description": "Redesign client website."
  }
  ```

- **GET /api/proposals//**: Retrieve a proposal.

- **PUT/PATCH /api/proposals//**: Update a proposal.

- **DELETE /api/proposals//**: Delete a proposal.

### Example API Request

```bash
curl -X POST http://localhost:8000/api/clients/ \
-H "Authorization: Bearer your_access_token" \
-H "Content-Type: application/json" \
-d '{"company_name": "Acme Corp", "email": "contact@acme.com"}'
```

## Testing

The project includes a comprehensive test suite using `pytest-django`.

1. **Run Tests**:

   ```bash
   pytest -v
   ```

2. **Test Coverage**:

   - `accounts/tests.py`: 26 tests for authentication (register, login, logout, profile).
   - `proposals/tests.py`: 21 tests for client and proposal APIs (CRUD, validation, authentication).
   - All tests pass, ensuring robust functionality.

## Admin Interface

- Access at `/admin/` with a superuser account.
- **Users**: Manage custom `User` model with autocomplete, search, and permission fields.
- **Clients**: List, filter, and search by `company_name`, `email`, `phone_number`; autocomplete for `added_by`.
- **Proposals**: List, filter, and search by `title`, `description`, `client`; autocomplete for `client` and `created_by`.

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

Please follow the code style guide and include tests for new features.

## Future Enhancements

- Add pagination and filtering for client/proposal lists.
- Implement file uploads for proposal documents.
- Introduce rate limiting for API endpoints.
- Add email notifications for proposal creation.
- Set up CI/CD with GitHub Actions.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

For questions or support, contact your.email@example.com.

---

- *Built with ❤️ using Django and Django REST Framework*