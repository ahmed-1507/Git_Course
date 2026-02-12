from urllib.parse import parse_qs
from xml.sax import parse
#
# from odoo.http import Controller, request, route
# import json
# import ast
#
#
# class ControlProductPrices(http.Controller):
#     @http.route('',auth='public')
#     def get_product_price(request):

from odoo import http

from odoo.http import Controller, request, route
import json
import ast
from odoo import fields, models, api, _, tools
from _socket import error

from odoo.exceptions import ValidationError,UserError




# لو عايز اهندل فانكشن لل valid and invalid results  هعملها هنا خارج الكلاس وانادي عليها جوه كل اندبوينت
def valid_response(data , status):
    response_body = {
        'message': 'success',
        'data': data
    }
    return request.make_json_response(response_body,status=status)


def invalid_response(error ,status):
    response_body = {
        'error': error,
    }
    return request.make_json_response(response_body,status=status)



class SubsEndPoints(http.Controller):
    # @http.route('saas_packages_info',auth='public')


    # اول معادله باستخدام ال type=http
    @http.route('/saas/create_record', methods=['GET', 'POST'], type='http', cors="*", auth='none',
                csrf=False)
    def create_record(self):
        args = request.httprequest.data.decode()
        vals = json.loads(args)                #  و args دي كده القيم اللي هدخلها في البوستمان يعني اللي اليوزر هيدخلها فهحولها من json الي dictionary باستخدام ال loads
        if not vals.get('name'):               # لو عايز اعمل فاليديشن علي اي فيلد required بحيث لو اليوزر مدخلش قيمه للفيلد ده يطلعله ايرور
            return request.make_json_response(
                {
                    'message': "name must be required !",
                }, status=400
            )
        try:       # بستخدمها لو عايز اهندل الايرور في حالة ظهوره
            res = request.env[''].sudo().create(vals)
            if res:
                return request.make_json_response(
                    {
                        'message': 'created successfully'
                    }, status=201
                )
        except Exception as error:
            return request.make_json_response(
                {
                    'message': error,
                }, status=400
            )


    # ثاني معادله باستخدام ال type=json
    @http.route('/saas/create_record_json', methods=['GET', 'POST'], type='json', cors="*", auth='none',
                csrf=False)
    def create_record_json(self):
        args = request.httprequest.data.decode()
        vals = json.loads(
            args)  # دي كده القيم اللي هدخلها في البوستمان يعني اللي اليوزر هيدخلها هحلوها من json الي dictionary باستخدام ال loads
        if not vals.get('name'):
            return {
                    'message': "name must be required !",
                }
        try:      # بستخدمها لو عايز اهندل الايرور في حالة ظهوره
            res = request.env[''].sudo().create(vals)
            if res:
                return {
                    'success':True,
                    'message': 'created successfully'
                }
        except Exception as error:
            return {
                    'message': error,
                }

    # <int:manager_id> ===> بتخلي الاي دي ديناميك علي حسب ما يختار اليوزر الريكورد اللي حابب يعدل فيه
    # والاي دي ده انا بكتبه كرقم في ال url زي كده 1/http://localhost:9015/api/test_endpoint_two
    @http.route('/saas/update_record/<int:manager_id>', methods=['PUT'], type='http', cors="*", auth='none',
                csrf=False)
    def update_record(self,manager_id):
        try:
            args = request.httprequest.data.decode()
            vals = json.loads(args)
            manager_id = request.env['manager.office'].sudo().search([('id', '=', manager_id)])
            if not manager_id:     # هنا هقوله يبحث في الريكوردات ال عندي بالاي دي اللي كتبه اليوزر ولو مش موجود ارفع ايرور
                return invalid_response(
                    {
                        'error': 'id not found',
                    }, status=400
                )
            else:
                manager_id.sudo().write(vals)
                return valid_response({'message': 'updated successfully'}, status=200)
        except Exception as error:
            return request.make_json_response(
                {
                    'message': error,
                }, status=400
            )


    @http.route('/saas/read_record/<int:manager_id>', methods=['GET'], type='http', cors="*", auth='none',
                csrf=False)
    def read_record(self,manager_id):
        try:
            manager_id = request.env['manager.office'].sudo().search([('id', '=', manager_id)])
            if not manager_id:
                return request.make_json_response(
                    {
                        'message': "id not exists !",
                    }, status=400
                )
            return request.make_json_response(
                {
                    'id': manager_id.id,
                    'name': manager_id.name,
                    'email': manager_id.email,
                    'phone': manager_id.phone,
                }, status=200
            )
        except Exception as error:
            return request.make_json_response(
                {
                    'error': error,
                }, status=400
            )


    @http.route('/saas/delete_record/<int:manager_id>', methods=['DELETE'], type='http', cors="*", auth='none',
                csrf=False)
    def delete_record(self, manager_id):
        try:
            manager_id = request.env['manager.office'].sudo().search([('id', '=', manager_id)])
            if not manager_id:
                return request.make_json_response(
                    {
                        'message': "id not exists !",
                    }, status=400
                )

            manager_id.unlink()
            return request.make_json_response(
                {
                    'message': 'deleted successfully'
                }, status=200
            )
        except Exception as error:
            return request.make_json_response(
                {
                    'error': error,
                }, status=400
            )


    @http.route('/saas/get_records', methods=['GET'], type='http', cors="*", auth='none',
                csrf=False)
    def get_records(self):
        try:
            #  لو عايز اجيب ال params اللي اليوزر هيدخلها هستخدم السطر ده وهترجعلي عباره عن  { ['value']:'key'}
            params = parse_qs(request.httprequest.query_string.decode('utf-8'))
            # params هنا هي خانة البارامز اللي في البوستمان .. يعني القيم اللي هدخلها في البوستمان هتظهر معايا هنا
            domain = []
            if params.get('key'):
                domain += [('key' , '=' ,params.get('key')[0])]
            manager_ids = request.env['manager.office'].sudo().search(domain)
            if not manager_ids:
                return request.make_json_response(
                    {
                        'message': "there are no records !",
                    }, status=400
                )
            return request.make_json_response(
                [{
                    'id': manager_id.id,
                    'name': manager_id.name,
                    'email': manager_id.email,
                    'phone': manager_id.phone,
                } for manager_id in manager_ids], status=200
            )
        except Exception as e:
            return request.make_json_response(
                {
                    'error': 'something went wrong!',
                }, status=400
            )


    @http.route('/saas/country_package_pricing', methods=['GET', 'POST'], type='json', cors="*", auth='public',
                csrf=False)
    def get_country_package_pricing(self, **kwargs):
        headers = request.httprequest.headers
        print('headers', headers.get('Content-Type', False))
        print('headers', headers.get('Content-Tyype', False))
        country_id = kwargs.get('country_id', False)
        country = country_id and request.env['res.country'].browse(int(country_id)) or False
        plan_id = kwargs.get('plan_id', False)
        plan = plan_id and request.env['sale.subscription.plan'].browse(int(plan_id)) or False
        saas_package_product = request.env['product.product'].sudo().search([('is_saas_package', '=', True)],
                                                                            order='id asc')
        main_saas_package_product = saas_package_product.filtered(lambda p: p.saas_package_id.package_type == 'main')
        additional_saas_package_product = saas_package_product.filtered(
            lambda p: p.saas_package_id.package_type == 'additional')
        print('saas_package_product', saas_package_product)
        # saas_package_product = request.env['product.template'].sudo().search([('is_saas_package', '=', True)])

        main_package_list = []

        for product in main_saas_package_product:
            pricing_dict = request.env['saas.subscription.mixin']._compute_price_unit(product_id=product,
                                                                                      country_id=country, plan_id=plan)
            main_package_list.append(
                {
                    'id': product.id,
                    'name': product.name,
                    'description': product.description_sale or product.description,
                    'package_type': product.saas_package_id.package_type,
                    'price': pricing_dict.get('price_unit'),
                    'currency': pricing_dict.get('currency'),
                    'recurring': product.recurring_invoice,
                }
            )
        additional_package_list = []
        for product in additional_saas_package_product:
            pricing_dict = request.env['saas.subscription.mixin']._compute_price_unit(product_id=product,
                                                                                      country_id=country, plan_id=plan)
            additional_package_list.append(
                {
                    'id': product.id,
                    'name': product.name,
                    'description': product.description_sale or product.description,
                    'package_type': product.saas_package_id.package_type,
                    'price': pricing_dict.get('price_unit'),
                    'currency': pricing_dict.get('currency'),
                    'recurring': product.recurring_invoice,
                }
            )
        return {
            'main': main_package_list,
            'additional': additional_package_list,

        }

    # @http.route('/saas/country_package_pricing', methods=['GET', 'POST'], type='json', cors="*", auth='public',
    #             csrf=False)
    # def get_country_package_pricing(self, **kwargs):
    #     headers = request.httprequest.headers
    #     print('headers', headers.get('Content-Type', False))
    #     print('headers', headers.get('Content-Tyype', False))
    #     country_id = kwargs.get('country_id', False)
    #     country = country_id and request.env['res.country'].browse(int(country_id)) or False
    #     plan_id = kwargs.get('plan_id', False)
    #     plan = plan_id and request.env['sale.subscription.plan'].browse(int(plan_id)) or False
    #     saas_package_product = request.env['product.product'].sudo().search([('is_saas_package', '=', True)],
    #                                                                         order='id asc')
    #     print('saas_package_product', saas_package_product)
    #     # saas_package_product = request.env['product.template'].sudo().search([('is_saas_package', '=', True)])
    #     product_list = []
    #     for product in saas_package_product:
    #         pricing_dict = request.env['saas.subscription.mixin']._compute_price_unit(product_id=product,
    #                                                                                   country_id=country, plan_id=plan)
    #         product_list.append({
    #             'id': product.id,
    #             'name': product.name,
    #             'description': product.description,
    #             'package_type': product.saas_package_id.package_type,
    #             'price': pricing_dict.get('price_unit'),
    #             'currency': pricing_dict.get('currency'),
    #             'recurring': product.recurring_invoice,
    #         })
    #     return product_list

    @http.route('/saas/action_create_pre_subscription', methods=['GET', 'POST'], type='json', cors="*", auth='public',
                csrf=False)
    def create_pre_subscription(self, **kwargs):

        pre_subscriptions_id = request.env['pre.subscription.payment.confirmation'].sudo()
        if kwargs.get('subscription_type') == 'new':

            required_data = ['country_id', 'plan_id', 'main_package','email']

            req_data_validate = list(filter(lambda d: not kwargs.get(d, False), required_data))
            if bool(req_data_validate):
                return {
                    'success': False,
                    'msg': f"Missing Required Data {req_data_validate}"
                }

        if  kwargs.get('subscription_type') in ['extend', 'renew']:

            required_data = ['subscription_id','email']
            req_data_validate = list(filter(lambda d: not kwargs.get(d, False), required_data))
            if bool(req_data_validate):
                return {
                    'success': False,
                    'msg': f"Missing Required Data {req_data_validate}"
                }

        main_saas_package_info = kwargs.get('main_package', {})
        additional_package_info = kwargs.get('additional_packages', [])
        pre_subscription_line_ids = [(0, 0, {
            'product_id': int(main_saas_package_info.get('id')),
            'discount': main_saas_package_info.get('discount'),

        })] + [(0, 0, {
            'product_id': int(add.get('id')),
            'discount': add.get('discount'),
        }) for add in additional_package_info]

        email = kwargs.get('email')
        partner_model = request.env['res.partner'].sudo()
        partner_id = partner_model.search([('email', '=', email)], limit=1, order='id desc')

        pre_sub_info = {
            'email': kwargs.get('email'),
            'partner_name': partner_id.name,
            'subscription_id': kwargs.get('subscription_id'),
            'country_id': int(kwargs.get('country_id')),
            'subscription_type': kwargs.get('subscription_type'),
            'plan_id': int(kwargs.get('plan_id')),
            'pre_subscription_line_ids': pre_subscription_line_ids,
            'main_saas_package_id': main_saas_package_info.get('id')

        }

        pre_subscription = request.env['pre.subscription.payment.confirmation'].sudo().create(pre_sub_info)
        return {
            'success': True,
            'pre_subscription_id': pre_subscription.id

        }

    @http.route('/saas/subscription_plans', methods=['GET', 'POST'], type='json', cors="*", auth='public', csrf=False)
    def get_subscription_plans(self, **kwargs):
        default_plan_id = request.env['ir.default'].sudo()._get('res.config.settings', 'front_end_default_plan')
        plans = request.env['sale.subscription.plan'].sudo().search([], order='id asc')
        return [{
            'id': plan.id,
            'name': plan.name,
            'billing_period_value': plan.billing_period_value,
            'billing_period_unit': plan.billing_period_unit,
            'discount': plan.discount,
            # 'billing_period_unit':plan.billing_period_unit,
            'is_default': plan.id == default_plan_id,
        } for plan in plans]

    @http.route('/saas/countries2', methods=['GET', 'POST'], type='http', cors="*", auth='public', csrf=False)
    def get_countries2(self):
        default_country = request.env['res.country'].sudo().search([('code', '=', 'SA')], order='id desc', limit=1)
        countries = request.env['res.country'].sudo().search([], order='name asc')
        return request.render('saas_subscription_managment.test_temp', {'cons': countries})

    @http.route('/saas/countries', methods=['POST', 'GET'], type='json', cors="*", auth='public', csrf=False,
                website=True)
    def get_countries(self, **kwargs):
        print('kwargs', kwargs)

    # @http.route('/saas/countries', methods=['POST', 'GET'], type='json',cors="*", auth='public',csrf=False,website=True)
    @http.route('/saas/countries', methods=['POST', 'GET'], type='json', cors="*", auth='public', website=True)
    def get_countries(self, **kwargs):
        print('kwargs', kwargs)

        default_country = request.env['res.country'].sudo().search([('code', '=', 'SA')], order='id desc', limit=1)
        countries = request.env['res.country'].sudo().search([], order='name asc')
        return [{
            'id': country.id,
            'name': country.name,
            'code': country.code,
            'phone_code': country.phone_code,
            'image': country.api_flag_image or country.get_api_flag_image(),
            'is_default': country.id == default_country.id,

        } for country in countries]

    @http.route('/saas/check_valid_subdomain', methods=['GET', 'POST'], type='json', cors="*", auth='public',
                csrf=False)
    def check_valid_subdomain(self, subdomain):
        stack_model = request.env['portainer.stack'].sudo()
        valid = True
        msg_lst = []
        existed_stacks = stack_model.search([('stack_technikal_name', '=', subdomain)])
        if existed_stacks.ids:
            valid = False
            msg_lst.append(f"The Subdomain '{subdomain}' Is Already Used, Please  Choose Another Subdomain")
        valid_chars, err_msg = stack_model.check_subdomain_validity(subdomain)
        if not valid_chars:
            valid = False
            msg_lst.append(err_msg)
        msg = '\n'.join(msg_lst)
        return {
            'valid': valid,
            'msg': msg,
        }

    @http.route('/saas/available_online_payment', methods=['GET', 'POST'], type='json', cors="*", auth='public',
                csrf=False)
    def get_available_online_payment(self):
        available_online_payment = request.env['ir.default'].sudo()._get('res.config.settings',
                                                                         'available_online_payment')
        return {
            'available_online_payment': available_online_payment,
        }

    @http.route('/saas/verify_email', methods=['POST', 'GET'], type='json', cors="*", auth='public', csrf=False)
    def verify_email(self, email, code):
        verified = True
        pre_subs_id = False
        msg_lst = []
        mail_verify_model = request.env['mail.verification'].sudo()
        to_verify_mail = mail_verify_model.search([('email', '=', email), ('state', '=', 'un_verified')],
                                                  order='id desc', limit=1)
        if not to_verify_mail.id:
            verified = False
            msg_lst.append('Mail Not Sent')
        else:
            verify_res = to_verify_mail.action_verify_code(code=str(code))
            verified = verify_res.get('valid', False)
            new_msg = verify_res.get('msg', '')
            pre_subs_id = verify_res.get('pre_subs_id', False)
            msg_lst.append(new_msg)
        print('msg list>>>>>>>',msg_lst)
        msg = '\n'.join(msg_lst)

        return {
            'verified': verified,
            'msg': msg,
            'pre_subs_id': pre_subs_id,
        }

    @http.route('/saas/action_register', methods=['POST', 'GET'], type='json', cors="*", auth='public',
                csrf=False)
    def send_verification_email(self, **kwargs):
        required_data = ['email', 'partner_name', 'phone', 'password', 'confirm_password', 'sub_domain', 'country_id',
                         'subscription_type', 'plan_id', 'pre_subscription_line_ids', 'company_name']
        not_sent_req_data = list(filter(lambda d: not kwargs.get(d, False), required_data))
        if bool(not_sent_req_data):
            return {
                'sent': False,
                'msg': f"Missing Required Data {not_sent_req_data}"
            }
        qty_pre_subs_line_ids = kwargs.get('pre_subscription_line_ids')
        qty_pre_subs_line_ids = list(map(lambda d:dict(d,quantity=d.get('quantity',1) or 1),qty_pre_subs_line_ids ))

        kwargs.update({
            'pre_subscription_line_ids' :qty_pre_subs_line_ids
        })
        email = kwargs.get('email')
        mail_verify_model = request.env['mail.verification'].sudo()
        last_mails = mail_verify_model.search([('email', '=', email)], order='id desc')
        mail_rec = mail_verify_model
        sent = True
        msg_lst = []
        if last_mails.ids:
            if any(m.state == 'verified' for m in last_mails):
                sent = False
                msg_lst.append(
                    f"This Email '{email}' Is Already Registered Before, You Can Sign In To See Your Dashboard Or Choos A Not Registered Email")
            else:
                mail_rec = last_mails[0]
                mail_rec.sudo().write({'pre_subscription_info': kwargs})
        else:
            mail_rec = mail_verify_model.create(
                {'email': email, 'state': 'un_verified', 'pre_subscription_info': kwargs})
        if mail_rec.id:
            sent, new_msg = mail_rec.send_verification_mail()
            msg_lst.append(new_msg)
        msg = '\n'.join(msg_lst)
        return {
            'sent': sent,
            'msg': msg,
        }

    @http.route('/saas/get_payment_attachment', methods=['GET', 'POST'], type='json', cors="*", auth='public',
                csrf=False)
    def get_payment_attachment(self, pre_subscription_id, attachment):
        domain = [('id', '=', pre_subscription_id)]
        pre_subscription_obj = request.env['pre.subscription.payment.confirmation'].sudo().search(domain)
        # pre_subscription_obj.payment_att = attachment
        msg_list = []
        state = pre_subscription_obj.state
        msg1 = "The process has been completed , please wait"
        msg2 = f" id ({pre_subscription_id}) Is Not Found"

        if pre_subscription_obj:
            try:
                pre_subscription_obj.write({
                    'payment_att':attachment
                })
                msg_list.append(msg1)
                msg = '\n'.join(msg_list)
                return {
                    'sent': True,
                    'msg': msg,
                    'state':state
                }
            except Exception as e :
                    return {"You Must Enter A Binary Value"}
        else:
            msg_list.append(msg2)
            msg = '\n'.join(msg_list)
            return {
                'sent':False,
                'msg':msg,
            }

    @http.route('/saas/set_promo_code', methods=['GET', 'POST'], type='json', cors="*", auth='public', csrf=False)
    def set_promo_code(self, pre_subscription_id, code):
        promo = request.env['promo.code'].sudo().search([('code', '=', code)])
        pre_subscription = request.env['pre.subscription.payment.confirmation'].sudo().browse(pre_subscription_id)
        pre_subscription.promo_code_id = promo.id

        return {
            'success':True ,
            'data': {
                'discount_percent %': promo.discount_percentage,
                'total_before_discount ': pre_subscription.price_total,
                'net_amount ': pre_subscription.net,
                'discount_amount ': pre_subscription.price_total - pre_subscription.net,
            }
        }

    @http.route('/saas/check_promo_code', methods=['GET', 'POST'], type='json', cors="*", auth='public', csrf=False)
    def check_promo_code_validate(self, **kwargs):
        code = kwargs.get('code')
        response = request.env['promo.code'].sudo().action_validate_promo_code(code=code)
        return response

    @http.route('/saas/edit_personal_information', methods=['GET', 'POST'], type='json', cors="*", auth='public', csrf=False)
    def edit_partner_personal_information(self, **kwargs):
        email = kwargs.get('email')
        partner_model = request.env['res.partner'].sudo()
        partner_id = partner_model.search([('email', '=', email)], limit=1, order='id desc')
        vals = {}
        msg1 = "Your Profile Data Has Been Updated"
        msg2 = _(f" Email ({kwargs.get('email')}) IS Not Exist")

        if partner_id:
            if kwargs.get('partner_name'):
                vals.update({'name': kwargs.get('partner_name')})

            if kwargs.get('phone'):
                vals.update({'phone': kwargs.get('phone')})

            try:
                partner_id.write({'image_1920': kwargs.get('profile_img')})
            except Exception as e:
                return ("Invalid Profile Image Data")

            partner_id.write(vals)
            return {
                'success': True,
                'msg': msg1,
            }
        else:
            return {
                'success': False,
                'msg': msg2,
            }

    @http.route('/saas/partner_login', methods=['GET', 'POST'], type='json', cors="*", auth='public', csrf=False)
    def action_saas_partner_login(self, email, password):
        mail_verify_model = request.env['mail.verification'].sudo()
        verified_mail = mail_verify_model.search([('email', '=', email), ('state', '=', 'verified')],
                                                 order='id desc', limit=1)
        login = True
        msg_lst = []
        if not verified_mail.id:
            login = False
            msg_lst.append('There Is No Registered Accoount For This Email')
        else:
            if not verified_mail.password == password:
                login = False
                msg_lst.append('Worng Password')
        msg = '\n'.join(msg_lst)
        return {
            'login': login,
            'msg': msg,
        }

    @http.route('/saas/forget_password', methods=['GET', 'POST'], type='json', cors="*", auth='public', csrf=False)
    def action_saas_forget_password(self, email):
        mail_verify_model = request.env['mail.verification'].sudo()
        verified_mail = mail_verify_model.search([('email', '=', email), ('state', '=', 'verified')],
                                                 order='id desc', limit=1)
        sent = True
        msg_lst = []
        if not verified_mail.id:
            sent = False
            msg_lst.append('There Is No Registered Accoount For This Email')
        else:
            verified_mail.action_forget_password()
            msg_lst.append('Please Check Your Email To Get Your New Password Code')
        msg = '\n'.join(msg_lst)
        return {
            'sent': sent,
            'msg': msg,
        }

    @http.route('/saas/change_password', methods=['GET', 'POST'], type='json', cors="*", auth='public', csrf=False)
    def action_saas_change_password(self, email, old_password, password, confirm_password):
        mail_verify_model = request.env['mail.verification'].sudo()
        verified_mail = mail_verify_model.search([('email', '=', email), ('state', '=', 'verified')],
                                                 order='id desc', limit=1)
        password_set = True
        msg_lst = []
        if not verified_mail.id:
            password_set = False
            msg_lst.append('There Is No Registered Accoount For This Email')
        else:
            reset_pass_details = verified_mail.action_change_passowrd(old_password=old_password, password=password,
                                                                      confirm_password=confirm_password)
            password_set = reset_pass_details.get('password_set', password_set)
            msg_lst.append(reset_pass_details.get('msg', ''))
        msg = '\n'.join(msg_lst)
        return {
            'password_set': password_set,
            'msg': msg,
        }

    @http.route('/saas/profile_subscription_data', methods=['GET', 'POST'], type='json', cors="*", auth='public',
                csrf=False)
    def get_profile_subscription_data(self, email):
        partner_model = request.env['res.partner'].sudo()
        partner_id = partner_model.search([('email', '=', email)], limit=1, order='id desc')
        subscription_model = request.env['sale.order'].sudo()
        subs_domain = [('subscription_state', 'not in', ['2_renewal', '5_renewed', '7_upsell', False]),
                       ('is_parent_subs', '=', True), ('partner_id', '=', partner_id.id)]
        subscription_ids = subscription_model.search(subs_domain)
        print('subscription_ids', subscription_ids)
        pre_subscription_model = request.env['pre.subscription.payment.confirmation'].sudo()
        subs_domain = ['|', ('partner_id', '=', partner_id.id), ('email', '=', email)]
        pre_subs_ids = pre_subscription_model.search(subs_domain)
        print('pre_subs_ids', pre_subs_ids)


        return ({

            'partner_details': [{
                'partner_image': partner.image_1920,
                'partner_name': partner.name,
                'partner_email': partner.email,
                'partner_phone': partner.phone,
                'partner_company_name': partner.company_name,
            } for partner in partner_id],

            'subscription_details': [{
                'main_packages_info': {
                       'id' : subs.main_saas_package_id.id ,
                       'name': subs.main_saas_package_id.name ,
                       'description': subs.main_saas_package_id.description,
                       'price_unit': subs.get_main_package_amount(),
                },

                'additional_packages_info': [{
                        'id': l.product_id.id,
                        'name': l.product_id.name,
                        'description': l.product_id.description,
                        'quantity': l.product_uom_qty,
                        'price_unit': l.price_unit,
                 } for l in subs.get_add_package_lines()],

                'users_details': {
                    'id': subs.get_saas_users_lines()[0].id if subs.get_saas_users_lines().ids else False,
                    'price_unit':subs.get_saas_users_lines()[0].price_unit if subs.get_saas_users_lines().ids else 0,
                'users_count': {
                'default_count':4,
                'additional_count': subs.get_additional_saas_users_count(),
                'total_count': 4 + subs.get_additional_saas_users_count()
                }

                } ,

                'subs_id': subs.id,
                'subs_name': subs.name,
                'subs_state': subs.plan_id.name,
                'subs_amount': subs.amount_total,
                'subs_renew_date': subs.next_invoice_date,
                'subs_date_order': subs.date_order,
                'db_link': subs.stack_id.partner_db_link,
            } for subs in subscription_ids],

            'billing_history': [{
                'bill_id': bill.id,
                'bill_name': bill.name,
                'bill_state': bill.state,
                'bill_amount': bill.net,
                'bill_creation_date': bill.create_date,
            } for bill in pre_subs_ids]

        })
