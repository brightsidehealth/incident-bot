import config

from bot.models.pg import OperationalData, Session
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

pager = Blueprint("pager", __name__)


@pager.route("/pager", methods=["GET"])
@jwt_required()
def get_pager():
    if config.pagerduty_integration_enabled != "false":
        try:
            data = (
                Session.query(OperationalData)
                .filter(OperationalData.id == "pagerduty_oc_data")
                .one()
                .serialize()
            )
            return (
                jsonify({"data": data["json_data"], "ts": data["updated_at"]}),
                200,
                {"ContentType": "application/json"},
            )
        except Exception as error:
            return (
                jsonify({"error": str(error)}),
                500,
                {"ContentType": "application/json"},
            )
        finally:
            Session.close()
            Session.remove()
    return (
        jsonify({"data": "feature_not_enabled"}),
        200,
        {"ContentType": "application/json"},
    )


@pager.route("/pager/auto_map", methods=["GET"])
@jwt_required()
def get_pager_automapping():
    if config.pagerduty_integration_enabled != "false":
        try:
            data = (
                Session.query(OperationalData)
                .filter(OperationalData.id == "pagerduty_auto_mapping")
                .one()
                .serialize()
            )
            return (
                jsonify({"data": data["json_data"], "ts": data["updated_at"]}),
                200,
                {"ContentType": "application/json"},
            )
        except Exception as error:
            return (
                jsonify({"error": str(error)}),
                500,
                {"ContentType": "application/json"},
            )
        finally:
            Session.close()
            Session.remove()
    return (
        jsonify({"data": "feature_not_enabled"}),
        200,
        {"ContentType": "application/json"},
    )


@pager.route("/pager/auto_map/store", methods=["GET", "PATCH"])
@jwt_required()
def get_patch_pager_automapping():
    if config.pagerduty_integration_enabled != "false":
        if request.method == "GET":
            try:
                data = (
                    Session.query(OperationalData)
                    .filter(OperationalData.id == "auto_page_teams")
                    .one()
                    .serialize()
                )
                return (
                    jsonify(
                        {"data": data["json_data"], "ts": data["updated_at"]}
                    ),
                    200,
                    {"ContentType": "application/json"},
                )
            except Exception as error:
                return (
                    jsonify({"error": str(error)}),
                    500,
                    {"ContentType": "application/json"},
                )
            finally:
                Session.close()
                Session.remove()
        elif request.method == "PATCH":
            v = request.json["value"]
            try:
                data = (
                    Session.query(OperationalData)
                    .filter(OperationalData.id == "auto_page_teams")
                    .one()
                )
                data.json_data = {"teams": v}
                Session.commit()
                return (
                    jsonify({"success": True}),
                    200,
                    {"ContentType": "application/json"},
                )
            except Exception as error:
                return (
                    jsonify({"error": str(error)}),
                    500,
                    {"ContentType": "application/json"},
                )
            finally:
                Session.close()
                Session.remove()
    return (
        jsonify({"data": "feature_not_enabled"}),
        200,
        {"ContentType": "application/json"},
    )
