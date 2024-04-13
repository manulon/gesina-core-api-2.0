from flask import Blueprint, jsonify, request

from src.service import activity_service

ACTIVITY_API_BLUEPRINT = Blueprint("activity", __name__, url_prefix="/activity")


@ACTIVITY_API_BLUEPRINT.get("/success_percentage")
def get_activity():
    date_from = request.args.get('date_from', None)
    date_to = request.args.get('date_to', None)
    labels, success_count, error_count = activity_service.get_activity_data(date_from,date_to)
    data = []
    for i in range(len(labels)):
        total_executions = success_count[i] + error_count[i]
        data.append({labels[i] : "No activity" if total_executions == 0 else int(100*(success_count[i] / total_executions))})
    return jsonify(data)

@ACTIVITY_API_BLUEPRINT.get("/average_time_execution")
def get_average_time_execution():
    labels, times = activity_service.get_execution_average_time_data()
    date_from = request.args.get('date_from', None)
    date_to = request.args.get('date_to', None)
    data = []
    for i in range(len(labels)):
        data.append({ labels[i] : times[i]})
    return jsonify(data)
