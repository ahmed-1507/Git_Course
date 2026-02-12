from odoo import http
from urllib.parse import parse_qs
from xml.sax import parse
from odoo.http import Controller, request, route
import json
import ast
from odoo import fields, models, api, _, tools
from _socket import error

from odoo.exceptions import ValidationError,UserError

class TestApi(http.Controller):

    @http.route('/api/test_endpoint', methods=['GET', 'POST'], type='http', cors="*", auth='none',csrf=False)
    def test_endpoint(self):
        print("print from inside test_endpoint method")
        args = request.httprequest.data.decode()
        vals = json.loads(args)
        print(">>>>>>>>>>>>>>>>>",vals)
        res = request.env['hospital.doctor'].sudo().create(vals)
        print(res)
        if res:
            return request.make_json_response(
                {
                    "status": "success",
                    "message": f"doctor {res.name} has been created successfully",
                }, status=201
            )


    @http.route('/api/test_endpoint_two',methods=['GET', 'POST'], type='json', cors="*", auth='none', csrf=False)
    def test_endpoint_two(self, **kwargs):
        print(">>> Inside test_endpoint_two endpoint")
        args = request.httprequest.data.decode()
        vals = json.loads(args)
        print(">>>>>>>>>>>>>>>>>", vals)
        res = request.env['hospital.doctor'].sudo().create(vals)
        print(res)
        if res:
            return {
                "status": "success",
                "message":  f"doctor {res.name} has been created successfully",
                "received_data": kwargs,
            }


    # @http.route('', methods=['GET', 'POST'], type='http', cors="*", auth='none',
    #             csrf=False)
    # def create_record(self):
    #     args = request.httprequest.data.decode()
    #     vals = json.loads(args)                #  دي كده القيم اللي هدخلها في البوستمان يعني اللي اليوزر هيدخلها هحلوها من json الي dictionary باستخدام ال loads
    #     if not vals.get('name'):
    #         return request.make_json_response(
    #             {
    #                 'message': "name must be required !",
    #             }, status=400
    #         )
    #     try:       # بستخدمها لو عايز اهندل الايرور في حالة ظهوره
    #         res = request.env[''].sudo().create(vals)
    #         if res:
    #             return request.make_json_response(
    #                 {
    #                     'message': 'created successfully'
    #                 }, status=201
    #             )
    #     except Exception as error:
    #         return request.make_json_response(
    #             {
    #                 'message': error,
    #             }, status=400
    #         )