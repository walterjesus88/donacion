# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError
import base64
import StringIO
import cStringIO
import json
# class Academy(http.Controller):
#     @http.route('/academy/academy/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

class Registrarse(http.Controller):

    @http.route(['/web/nuevo_usuario'], type='http', auth="public", methods=['GET', 'POST'], website=True)
    def web_nuevo_usuario(self, **post):
        if post:
            login = post.get('email', False)
            # password = post.get('password', False)
            # password2 = post.get('password2', False)
            email = post.get('email', False)
            name_filename=post['documento'].filename
            dd = post.get('documento', False)            
            data=dd.read()            
            documento= base64.encodestring(data)

            #documentos en caso de  ONG
            name_apci=post['apci'].filename
            apci=post.get('apci',False)
            d_apci=apci.read()
            documento_apci=base64.encodestring(d_apci)


            name_entidades=post['entidades'].filename
            entidades=post.get('entidades',False)
            d_entidades=entidades.read()
            documento_entidades=base64.encodestring(d_entidades)


            telefonop = post.get('telefonop', False)
            telefonoi = post.get('telefonoi', False)
            persona = post.get('persona', False)
            dni = post.get('dni', False)
            tipo = post.get('tipo', False)
            institucion = post.get('institucion', False)
            direccioninstitucion = post.get('direccioninstitucion', False)
            direccionpersonal = post.get('direccionpersonal', False)
           
            # buff=cStringIO.StringIO()
            # buff.write(data)
            # buff.seek(0)

            # f = open('/tmp/te4st.pdf', 'wb')
            # f.write(buff.read())
            # f.close()

          
            #if login and password and password2 and password == password2 and email :
            if login and email :
                # db = request.cr.dbname
                #res_users = http.request.env['res.users']           
                res_users = http.request.env['donacion.usuario'].sudo()          

                dict_partner=dict(
                    name=institucion,
                    email=email, 
                    docautoriza=documento,
                    mobile=telefonop,
                    phone=telefonoi,                    
                    persona=persona,                    
                    dni=dni,                    
                    tipo=tipo,                    
                    institucion=institucion,                    
                    direccioninstitucion=direccioninstitucion,                    
                    direccionpersonal=direccionpersonal,  

                    documento_apci=documento_apci,
                    name_apci=name_apci,
                    documento_entidades=documento_entidades,
                    name_entidades=name_entidades,
                )


                #print('dict_partner')

                if not res_users.search([('login', '=', login)]).id:
               
                    user = res_users.get_or_create_user(login, documento,name_filename, dict_partner=dict_partner)
                   
                    if user:
                        print('user.id')
                        print(user)
                        #pdb.set_trace()
                 

                        return request.render('donacion.signin_notificacion_usuario', {})

             


                # else:
                #         return {
                #             'type': 'ir.actions.client',
                #             'tag': 'action_warn',
                #             'name': _('Aviso'),
                #             'context' : context,
                #             'params': {
                #                'title': _('Aviso'),
                #                'text': _(u'Mensaje para el usuario'),
                #                'sticky': True
                #            }}

        return request.render('donacion.form_nuevo_usuario', {})


    @http.route(['/page/requirement'], type='http', auth="public", methods=['GET', 'POST'], website=True)
    def web_inicio(self, **post):
        return request.render('donacion.index', {})














