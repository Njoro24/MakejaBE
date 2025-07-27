import uuid
from datetime import datetime
from sqlalchemy.orm.query import Query
import os
from werkzeug.utils import secure_filename


def generate_slug(value):
    return f"{value.lower().replace(' ', '-')}-{uuid.uuid4().hex[:6]}"


def format_datetime(value):
    return datetime.fromisoformat(str(value)).strftime("%Y-%m-%d %H:%M:%S")


def paginate_query(query: Query, page: int, per_page: int):
    return query.paginate(page=page, per_page=per_page, error_out=False)



def is_allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def rename_file(original_filename):
    ext = original_filename.rsplit('.', 1)[1].lower()
    return f"{uuid.uuid4().hex}.{ext}"
