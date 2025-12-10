# QWERTY Django Shop

A modern e-commerce platform for mechanical keyboards, keycaps, and accessories built with Django and a brutalist design aesthetic.

## Tech Stack

**Backend:** `Django 5.2.9` | `Python 3.11` | `PostgreSQL 17` | `Redis` | `Celery` | `RabbitMQ`

**Frontend:** `HTMX` | `TailwindCSS 4`

**Payment:** `Stripe API`

**Infrastructure:** `Docker` | `Nginx` | `Gunicorn` | `Traefik`

**Additional:** `WeasyPrint` | `Pillow` | `django-filter`

## Features

- **Product Catalog** with filtering, search, and sorting
- **Variant System** for product attributes (colors, switches, sizes)
- **Shopping Cart** with session-based persistence
- **Coupon System** for discounts
- **Stripe Integration** for secure payments
- **Order Management** with PDF invoice generation
- **Product Recommendations** using Redis
- **Async Task Processing** with Celery
- **Admin Dashboard** for inventory management

## Project Structure

```
qwerty/
├── apps/
│   ├── cart/          # Shopping cart functionality
│   ├── catalog/       # Product catalog & models
│   ├── coupons/       # Discount coupon system
│   ├── orders/        # Order processing
│   ├── pages/         # Static pages (home, about)
│   └── payment/       # Stripe payment integration
├── config/            # Django settings & configuration
├── templates/         # HTML templates
├── static/            # Static files (CSS, JS, images)
├── media/             # User-uploaded files
└── docker-compose.yml
```

## Quick Start

### Development (with DevContainer)

1. **Clone the repository**
   ```bash
   git clone https://github.com/x0ryz/qwerty.git
   cd qwerty
   ```

2. **Create `.env` file**
   ```env
   SECRET_KEY=your-secret-key
   DEBUG=True
   POSTGRES_DB=qwerty_db
   POSTGRES_USER=qwerty_user
   POSTGRES_PASSWORD=qwerty_password
   POSTGRES_HOST=db
   POSTGRES_PORT=5432
   REDIS_HOST=redis
   REDIS_PORT=6379
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

3. **Open in DevContainer**
   - Open project in VS Code
   - Click "Reopen in Container" when prompted
   - Services will start automatically

4. **Run migrations**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Access the application**
   - Web: http://localhost:8000
   - Admin: http://localhost:8000/admin

### Production Deployment

1. **Update `.env` for production**
   ```env
   DEBUG=False
   ALLOWED_HOSTS=your-domain.com
   CSRF_TRUSTED_ORIGINS=https://your-domain.com
   ```

2. **Deploy with Docker Compose**
   ```bash
   docker compose up -d --build
   ```

3. **Run initial setup**
   ```bash
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py createsuperuser
   docker compose exec web python manage.py collectstatic --noinput
   ```

## Key Components

### Product Variants
Products support multiple attributes (color, size, switch type) with dynamic variant selection and image galleries.

### Cart System
Session-based cart with coupon support and price calculations.

### Payment Flow
1. User creates order
2. Redirected to Stripe Checkout
3. Webhook confirms payment
4. Order marked as paid
5. Invoice sent via email

### Recommendation Engine
Redis-powered product recommendations based on purchase history.

### Async Tasks
- Email notifications (Celery)
- PDF invoice generation (WeasyPrint)
- Payment confirmation processing
