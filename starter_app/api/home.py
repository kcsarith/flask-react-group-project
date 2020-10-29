from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from starter_app.models import db, User, Restaurant, Review

bp = Blueprint("home", __name__)


@bp.route('/', methods=["POST"])
def search():
    term = request.get_json()
    search_args = [col.ilike('%%%s%%' % term) for col in
                   ['name', 'address', 'city', 'avg_rating', 'max_price']]
    restaurants = Restaurant.query.filter(or_(*search_args)).all()
    ordered_rests = restaurants.order_by(Restaurant.avg_rating.desc())
    return {'restaurants': [rest.to_dict() for rest in ordered_rests]}


@login_required
@bp.route('/<int:id>')
def index(id):
    response = User.query.get(id)
    user_rest = response.to_dict()
    rest_list = Restaurant.query.filter_by(city=user_rest['city']).all()
    return {'restaurants': [rest.to_dict() for rest in rest_list]}


@login_required
@bp.route('/restaurant/<int:rest_id>', methods=["GET", "POST"])
def reviews(rest_id):
    rest = Restaurant.query.get(rest_id)
    if not rest:
        return {"errors": ["Invalid restaurant requested"]}, 401
    if request.method == "POST":
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400
        content = request.json.get("content", None)
        rating = request.json.get("rating", None)
        if not content or not rating:
            return {"errors": ["Please fill out review and rating"]}, 400
        new_review = Review(restaurant_id=rest_id, user_id=current_user.id,
                            content=content, rating=rating)
        db.session.add(new_review)
        db.session.commit()
    response = Review.query.filter_by(restaurant_id=rest_id).all()
    return {'reviews': [review.to_dict() for review in response]}


@login_required
@bp.route('/restaurant/profile/<int:rest_id>')
def profile(rest_id):

    response = Restaurant.query.filter_by(id=rest_id).first()

    return {'restaurant': response.to_dict()}