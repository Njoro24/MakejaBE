import pytest
from app.models import Review, User, Hostel  

@pytest.fixture
def test_user(db):
    
    user = User(id=1, username="test_user") if 'User' in globals() else None
    if user:
        db.session.add(user)
        db.session.commit()
    return user

@pytest.fixture
def test_hostel(db):
   
    hostel = Hostel(id=1, name="Test Hostel") if 'Hostel' in globals() else None
    if hostel:
        db.session.add(hostel)
        db.session.commit()
    return hostel

@pytest.fixture
def test_review(db, test_user, test_hostel):
    review = Review(user_id=test_user.id, hostel_id=test_hostel.id, rating=4, comment="Good hostel")
    db.session.add(review)
    db.session.commit()
    return review

def test_create_review(client, auth_token, test_user, test_hostel):
    
    if not test_user or not test_hostel:
        pytest.skip("User/Hostel models not available")
    
    response = client.post(
        '/api/reviews',
        json={'hostel_id': test_hostel.id, 'rating': 5, 'comment': 'Great!'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 201
    assert Review.query.count() == 1

def test_admin_delete_review(client, admin_auth_token, test_review):
    response = client.delete(
        f'/api/admin/reviews/{test_review.id}',
        headers={'Authorization': f'Bearer {admin_auth_token}'}
    )
    assert response.status_code == 200
    assert Review.query.count() == 0
