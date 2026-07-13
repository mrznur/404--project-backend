# 404 Project Not Found — Backend

Django REST Framework backend for the Task Management + Image Annotation app.

---

## Authentication System

### 1. Changes Made
- Created `accounts/` app with `views.py`, `serializers.py`, `urls.py`
- Added `LoginView`, `LogoutView`, `MeView` in `accounts/views.py`
- Added `LoginSerializer`, `UserSerializer` in `accounts/serializers.py`
- Registered JWT endpoints in `accounts/urls.py`
- Configured `SIMPLE_JWT` in `config/settings.py`
- Created management command `accounts/management/commands/create_demo_user.py`

### 2. Connection Segment
- Frontend `/login` page → calls `POST /api/auth/login/` with `{email, password}`
- `LoginView.post()` → `LoginSerializer.validate()` → authenticates using Django's `authenticate()` → generates JWT via `RefreshToken.for_user(user)`
- Tokens stored in frontend `localStorage` → sent as `Authorization: Bearer <token>` on every protected request
- `api.ts` request interceptor attaches token automatically to every axios call
- 401 response interceptor clears localStorage and redirects to `/login`

### 3. Explanation Segment
- Django's built-in `User` model is used (no custom model needed)
- Email-based login: `LoginSerializer` looks up user by email (`User.objects.get(email=email)`), then calls `authenticate(username=user.username, password=password)`
- `SimpleJWT` generates access token (7-day lifetime) and refresh token (30-day)
- Frontend stores `access_token`, `refresh_token`, `user` in localStorage
- All protected views require `IsAuthenticated` permission class which validates the JWT

### 4. Difficulties / Villains Faced
- Django uses username for authentication by default, not email. Solved by looking up the User by email first, then authenticating with the username.
- CORS must allow credentials for JWT to work properly. Solved via `CORS_ALLOW_CREDENTIALS = True` in settings.

### 5. How to Test This Part
1. Start backend: `python manage.py runserver`
2. POST to `http://localhost:8000/api/auth/login/` with `{"email":"demo@example.com","password":"demo1234"}`
3. Should return `{access: "...", refresh: "...", user: {...}}`
4. Use access token as `Authorization: Bearer <token>` header on subsequent requests
5. GET `http://localhost:8000/api/auth/me/` with the token — should return user info

---

## Task Management API

### 1. Changes Made
- Created `tasks/` app with `models.py`, `serializers.py`, `views.py`, `urls.py`
- `Task` model with: `title`, `description`, `status`, `priority`, `due_date`, `tags`, `order`, `user` FK
- Three serializers: `TaskSerializer` (read), `TaskCreateUpdateSerializer` (write), `TaskStatusUpdateSerializer` (drag-drop)
- Three views: `TaskListCreateView`, `TaskDetailView`, `TaskStatusUpdateView`

### 2. Connection Segment
- Frontend `tasksApi.getByDate(date)` → `GET /api/tasks/?date=YYYY-MM-DD`
- Frontend `tasksApi.create(task)` → `POST /api/tasks/`
- Frontend `tasksApi.update(id, task)` → `PUT /api/tasks/<id>/`
- Frontend `tasksApi.delete(id)` → `DELETE /api/tasks/<id>/`
- Frontend drag-drop `tasksApi.updateStatus(id, status, order)` → `PATCH /api/tasks/<id>/status/`
- All views filter by `request.user` to ensure data isolation between users
- `DateContext` in frontend controls which date is sent as `?date=` parameter

### 3. Explanation Segment
- Tasks are filtered by `due_date` per request (not loaded all at once)
- `tags` stored as comma-separated string in DB; `tags_list` computed field splits it for frontend
- `order` field enables within-column sorting after drag-and-drop
- `status` is a CharField with choices: `todo`, `in_progress`, `done`
- Status update uses `PATCH` to update only `status` and `order` fields efficiently

### 4. Difficulties / Villains Faced
- date parsing: `parse_date()` from `django.utils.dateparse` handles YYYY-MM-DD cleanly.
- User data isolation: always filter `Task.objects.filter(user=request.user)` to prevent cross-user access.

### 5. How to Test This Part
1. Login and get access token
2. POST to `/api/tasks/` with `{"title":"Test","status":"todo","priority":"medium","due_date":"2024-12-25"}`
3. GET `/api/tasks/?date=2024-12-25` — should return the task
4. PATCH `/api/tasks/<id>/status/` with `{"status":"done","order":0}` — should update column
5. DELETE `/api/tasks/<id>/` — should remove it

---

## Image & Annotation API

### 1. Changes Made
- Created `annotations/` app with `models.py`, `serializers.py`, `views.py`, `urls.py`
- `UploadedImage` model: `user` FK, `image` (ImageField), `filename`, `width`, `height`, `uploaded_at`
- `Annotation` model: `image` FK, `label`, `points` (JSONField), `created_at`
- Custom `image_upload_path()` stores files at `media/images/<user_id>/<filename>`
- `MEDIA_URL` and `MEDIA_ROOT` configured in `config/settings.py`

### 2. Connection Segment
- Frontend `imagesApi.upload(file)` → `POST /api/annotations/images/upload/` (multipart/form-data)
- Frontend `imagesApi.list()` → `GET /api/annotations/images/`
- Frontend `imagesApi.get(id)` → `GET /api/annotations/images/<id>/`
- Frontend `imagesApi.delete(id)` → `DELETE /api/annotations/images/<id>/`
- Frontend `annotationsApi.create(imageId, data)` → `POST /api/annotations/images/<id>/annotations/`
- Frontend `annotationsApi.delete(id)` → `DELETE /api/annotations/<id>/`
- `UploadedImageSerializer.get_image_url()` uses `request.build_absolute_uri()` to return full URL
- Deleting an image calls model's custom `delete()` method which removes the file from disk

### 3. Explanation Segment
- Polygon coordinates stored as JSON array of `{x, y}` objects in `points` JSONField
- Coordinates are percentage-based (0-100) relative to image dimensions for resolution independence
- `AnnotationSerializer.validate_points()` enforces minimum 3 points and correct structure
- Image upload uses `MultiPartParser` and `FormParser`
- `Pillow` reads image dimensions after upload and stores them in `width`/`height`

### 4. Difficulties / Villains Faced
- Media files need Django's `static()` url helper in `config/urls.py` to be served in dev mode.
- JSON field for polygon points requires validation — done in `validate_points()` serializer method.
- Coordinates as percentages (not pixels) means annotations remain valid regardless of display size.

### 5. How to Test This Part
1. Login and get access token
2. POST to `/api/annotations/images/upload/` with form-data `image=<file>` — returns image object with URL
3. GET `/api/annotations/images/` — list all your images
4. POST to `/api/annotations/images/<id>/annotations/` with `{"label":"car","points":[{"x":10,"y":10},{"x":50,"y":10},{"x":30,"y":50}]}`
5. GET `/api/annotations/images/<id>/` — image detail includes annotations array
6. DELETE `/api/annotations/<annotation_id>/` — removes just that polygon

---

## Backend Environment

- Python version: 3.12
- Django version: 6.0.6
- Database: SQLite (db.sqlite3)
- Main packages: djangorestframework 3.17.1, djangorestframework-simplejwt 5.5.1, django-cors-headers 4.9.0, Pillow 12.3.0
- API framework: Django REST Framework

## How to Run Backend

```bash
# 1. Create virtual environment
cd backend
python -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Create demo user
python manage.py create_demo_user
# Demo credentials:
#   Email: demo@example.com
#   Password: demo1234

# 6. Run development server
python manage.py runserver 8000

# 7. Media file setup
# Media files are served at http://localhost:8000/media/ in development.
# The media/ folder is created automatically when the first image is uploaded.

# 8. Deployment notes
# - Set DEBUG=False in production
# - Set a strong SECRET_KEY
# - Configure ALLOWED_HOSTS with your domain
# - Use a production WSGI server (gunicorn)
# - Serve media files via nginx/S3 in production
# - Update CORS_ALLOWED_ORIGINS with your frontend URL
```

---

## Image Storage — Base64 in Database

### Why Base64?
Vercel's serverless filesystem is ephemeral — files saved to `/tmp` disappear between requests. Instead of using an external service (S3, Cloudinary), we store images directly in the SQLite database as Base64-encoded strings.

### How it works
1. User uploads an image via `POST /api/annotations/images/upload/`
2. Backend reads the raw bytes, encodes to Base64, prepends the MIME type
3. Stores as: `data:image/jpeg;base64,/9j/4AAQ...`
4. Frontend receives this string as `image_url`
5. HTML `<img src="data:image/jpeg;base64,...">` renders it directly — no HTTP request needed

### Tradeoffs
- ✅ Works on Vercel without any external service
- ✅ Images persist in the database (SQLite)
- ✅ No CORS issues — data URIs are same-origin
- ⚠️ Larger database size (~33% bigger than raw file)
- ⚠️ 10MB file limit enforced in serializer

### Files Changed
- `annotations/models.py` — replaced `ImageField` with `TextField` for `image_data`
- `annotations/serializers.py` — `ImageUploadSerializer` reads file bytes, encodes Base64
- `annotations/views.py` — simplified, no more filesystem operations
- `annotations/migrations/0001_initial.py` — fresh migration for new model
