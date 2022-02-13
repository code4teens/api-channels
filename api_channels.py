from flask import Blueprint, jsonify, request
from sqlalchemy import exc

from database import db_session
from models import Channel, Cohort, User
from schemata import ChannelSchema

api_channels = Blueprint('api_channels', __name__)


@api_channels.route('/channels')
def get_channels():
    channels = Channel.query.order_by(Channel.id).all()
    data = ChannelSchema(many=True).dump(channels)

    return jsonify(data), 200


@api_channels.route('/channels', methods=['POST'])
def create_channel():
    keys = ['id', 'name', 'user_id', 'cohort_id']

    if sorted([key for key in request.json]) == sorted(keys):
        user_id = request.json.get('user_id')
        cohort_id = request.json.get('cohort_id')
        user = User.query.filter_by(id=user_id).one_or_none()
        cohort = Cohort.query.filter_by(id=cohort_id).one_or_none()

        if user is not None and cohort is not None:
            existing_channel = Channel.query.filter_by(user_id=user_id)\
                .filter_by(cohort_id=cohort_id)\
                .one_or_none()

            if existing_channel is None:
                channel_schema = ChannelSchema()

                try:
                    channel = channel_schema.load(request.json)
                except Exception as _:
                    data = {
                        'title': 'Bad Request',
                        'status': 400,
                        'detail': 'Some values failed validation'
                    }

                    return data, 400
                else:
                    db_session.add(channel)
                    db_session.commit()
                    data = {
                        'title': 'Created',
                        'status': 201,
                        'detail': f'Channel {channel.id} created'
                    }

                    return data, 201
            else:
                data = {
                    'title': 'Conflict',
                    'status': 409,
                    'detail': 'Channel with posted details already exists'
                }

                return data, 409
        else:
            data = {
                'title': 'Bad Request',
                'status': 400,
                'detail': 'User or cohort does not exist'
            }

            return data, 400

    else:
        data = {
            'title': 'Bad Request',
            'status': 400,
            'detail': 'Missing some keys or contains extra keys'
        }

        return data, 400


@api_channels.route('/channels/<int:id>')
def get_channel(id):
    channel = Channel.query.filter_by(id=id).one_or_none()

    if channel is not None:
        data = ChannelSchema().dump(channel)

        return data, 200
    else:
        data = {
            'title': 'Not Found',
            'status': 404,
            'detail': f'Channel {id} not found'
        }

        return data, 404


@api_channels.route('/channels/<int:id>', methods=['PUT'])
def update_channel(id):
    keys = ['name', 'user_id', 'cohort_id']

    if all(key in keys for key in request.json):
        existing_channel = Channel.query.filter_by(id=id).one_or_none()

        if existing_channel is not None:
            channel_schema = ChannelSchema()

            try:
                channel = channel_schema.load(request.json)
            except Exception as _:
                data = {
                    'title': 'Bad Request',
                    'status': 400,
                    'detail': 'Some values failed validation'
                }

                return data, 400
            else:
                channel.id = existing_channel.id
                db_session.merge(channel)

                try:
                    db_session.commit()
                except exc.IntegrityError as _:
                    data = {
                        'title': 'Bad Request',
                        'status': 400,
                        'detail': 'Some values failed validation'
                    }

                    return data, 400
                else:
                    data = channel_schema.dump(existing_channel)

                    return data, 200
        else:
            data = {
                'title': 'Not Found',
                'status': 404,
                'detail': f'Channel {id} not found'
            }

            return data, 404
    else:
        data = {
            'title': 'Bad Request',
            'status': 400,
            'detail': 'Missing some keys or contains extra keys'
        }

        return data, 400


@api_channels.route('/channels/<int:id>', methods=['DELETE'])
def delete_channel(id):
    channel = Channel.query.filter_by(id=id).one_or_none()

    if channel is not None:
        db_session.delete(channel)
        db_session.commit()
        data = {
            'title': 'OK',
            'status': 200,
            'detail': f'Channel {id} deleted'
        }

        return data, 200
    else:
        data = {
            'title': 'Not Found',
            'status': 404,
            'detail': f'Channel {id} not found'
        }

        return data, 404
