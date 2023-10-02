from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from src.database.database import db, Bookmark
from src.constants.http_status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_201_CREATED, HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT
import validators

bookmarks = Blueprint('bookmarks', __name__, url_prefix='/api/v1/bookmarks')


@bookmarks.get('/')
@bookmarks.post('/')
@jwt_required()
def bookmarker():
    current_user = get_jwt_identity()
    if request.method == 'POST':
        body = request.json.get('body', '')
        url = request.get_json().get('url', '')

        if not validators.url(url):
            return jsonify({'status': 400, 'message': 'Invalid url', 'data': None}), HTTP_400_BAD_REQUEST
        
        if Bookmark.query.filter_by(url=url).first():
            return jsonify({'status': 409, 'message': 'The URL has previously been saved', 'data': None}), HTTP_409_CONFLICT
        
        bookmarked = Bookmark(body=body, url=url, user_id=current_user)
        db.session.add(bookmarked)
        db.session.commit()

        return jsonify({
            'status': 201,
            'message': 'URL bookmarked succesfully',
            'data': {
                'URL': bookmarked.url,
                'id': bookmarked.id,
                'short_url': bookmarked.short_url,
                'visits': bookmarked.visits,
                'created_at': bookmarked.created_at,
                'updated_at': bookmarked.updated_at
            }
        }), HTTP_201_CREATED

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    bookmarks = Bookmark.query.filter_by(user_id=current_user).paginate(page=page, per_page=per_page)
    data = []

    for bookmark in bookmarks.items:
        data.append({
            'id': bookmark.id,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visit': bookmark.visits,
            'body': bookmark.body,
            'created_at': bookmark.created_at,
            'updated_at': bookmark.updated_at
        })

    meta = {
        'page': bookmarks.page,
        'pages': bookmarks.pages,
        'total_count': bookmarks.total,
        'prev_page': bookmarks.prev_num,
        'next_page': bookmarks.next_num,
        'has_next': bookmarks.has_next,
        'has_prev': bookmarks.has_prev
    }

    if len(data) > 0:
        return jsonify({'status': 200, 'message': 'Retrieve succesful', 'data': data, 'meta': meta}), HTTP_200_OK
    else:
        return jsonify({'status': 200, 'message': 'No url records yet', 'data': None}), HTTP_200_OK


@bookmarks.get('/<int:id>')
@jwt_required()
def get_bookmark(id):
    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return jsonify({'status': 404, 'message': 'Bookamrk not found', 'data': None}), HTTP_404_NOT_FOUND
    
    return jsonify({
        'status': 200,
        'message': 'Retrieve succesful',
        'data': {
            'id': bookmark.id,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visit': bookmark.visits,
            'body': bookmark.body,
            'created_at': bookmark.created_at,
            'updated_at': bookmark.updated_at
        }
    }), HTTP_200_OK



@bookmarks.put('/<int:id>')
@bookmarks.patch('/<int:id>')
@jwt_required()
def update_bookamrk(id):
    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return jsonify({'status': 404, 'message': 'Bookamrk not found', 'data': None}), HTTP_404_NOT_FOUND
    
    body = request.json.get('body', '')
    url = request.get_json().get('url', '')

    if not validators.url(url):
        return jsonify({'status': 400, 'message': 'Invalid url', 'data': None}), HTTP_400_BAD_REQUEST
    
    bookmark.url = url
    bookmark.body = body

    db.session.commit()

    return jsonify({
            'status': 200,
            'message': 'URL updated succesfully',
            'data': {
                'URL': bookmark.url,
                'id': bookmark.id,
                'short_url': bookmark.short_url,
                'visits': bookmark.visits,
                'created_at': bookmark.created_at,
                'updated_at': bookmark.updated_at
            }
        }), HTTP_200_OK


@bookmarks.delete('/<int:id>')
@jwt_required()
def delete_bookmark(id):
    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return jsonify({'status': 404, 'message': 'Bookamrk not found', 'data': None}), HTTP_404_NOT_FOUND
    
    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({}), HTTP_204_NO_CONTENT


@bookmarks.get('/stats')
@jwt_required()
@swag_from('./docs/bookmarks/stats.yaml')
def get_stats():
    current_user = get_jwt_identity()

    data = []
    
    items = Bookmark.query.filter_by(user_id=current_user).all()

    for item in items:
        data.append({
            'visits': item.visits,
            'url': item.url,
            'short_url': item.short_url,
            'id': item.id
        })

    return jsonify({'data': data}), HTTP_200_OK
