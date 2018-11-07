from flask import request, Blueprint, jsonify, render_template
from sqlalchemy import engine

import json_text_constants as j_const
import sql_abstract_builder as sql_bld
from app import db

organizers_handler = Blueprint(
    'organizers_handler', __name__, url_prefix='/api/organizer'
    )


@organizers_handler.route('/view/all')
def organizers_view_all():
    result_sys = db.execute(
        'SELECT * FROM organizers'
        )
    result = [dict(row) for row in result_sys]
    return render_template('organizers_list.html', attributes=result)


@organizers_handler.route('/view', methods=['GET'])
def organizer_view_specific():
    if len(request.args) == 0:
        return organizers_view_all()

    sql_statement = sql_bld.build_select_with_multiple_conditions(
        table='organizers',
        parameters=j_const.all_organizer_properties,
        arguments=request.args
        )

    if sql_statement is not None:
        result = db.execute(sql_statement)
        return jsonify({'result': [dict(row) for row in result]})
    else:
        return 'no one correct json key found'


@organizers_handler.route('/add', methods=['POST'])
def organizer_add():
    content = dict(request.get_json())
    organizer_id, name, address = get_organizer_data(content)
    if not_exists(organizer_id):
        sql_statement = sql_bld.build_insert_of_single_entry(
            table='organizers',
            values=(organizer_id, str(name), str(address))
            )
        db.execute(sql_statement)
        return 'ok'
    else:
        return 'organizer with such id already exists!'


@organizers_handler.route('/modify/<organizer_id>', methods=['POST'])
def organizer_modify(organizer_id):
    """
    required json: data_to_change (can not include ID)
    """
    if not_exists(organizer_id):
        return 'id not exists'

    json_dict = dict(request.get_json())
    if json_dict.get('id') is not None:
        return 'you can not modify organizer\'s ID!'

    sql_statement = f'UPDATE organizers SET '
    more_than_one_argument = False
    for i in j_const.all_organizer_properties:
        argument = json_dict.get(i)
        if argument is not None:
            if more_than_one_argument:
                sql_statement += ' , '
            sql_statement += f'{i} = {argument}'
            more_than_one_argument = True
    sql_statement += f'WHERE id = {organizer_id}'
    db.execute(sql_statement)
    return 'ok'


def not_exists(organizer_id):
    sql_statement = f'SELECT * FROM organizers ' \
                    f'WHERE ID = {organizer_id}'
    result: engine.ResultProxy = db.execute(sql_statement)
    return result.rowcount == 0


def get_organizer_data(content):
    name = content.get(j_const.organizer_name)
    address = content.get(j_const.organizer_address)
    organizer_id = content.get(j_const.organizer_id)
    return organizer_id, name, address


