# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError
import base64
import StringIO
import cStringIO
import json
import werkzeug 
#import generate_password_hash, check_password_hash
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
                res_users = http.request.env['res.users']           
                #res_users = http.request.env['donacion.usuario'].sudo()          

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


                if not res_users.search([('login', '=', login)]).id:
               
                    user = res_users.get_or_create_user(login, documento,name_filename, dict_partner=dict_partner)
                   
                    if user:
                        print('user.id')
                        print(user)
                        #pdb.set_trace()                 

                        return request.render('donacion.signin_notificacion_usuario', {})

             
        return request.render('donacion.form_nuevo_usuario', {})


    @http.route(['/page/requirement'], type='http', auth="public", methods=['GET', 'POST'], website=True)
    def web_inicio(self, **post):
        return request.render('donacion.index', {})


    # @http.route(['/page/requimision'], type='http', auth="public", methods=['GET', 'POST'], website=True)
    # def web_mision(self, **post):
    #     return request.render('donacion.mision', {})



    #class Attachment_Controller(http.Controller):

    #@http.route(['/attachment/token/<string:token>/download'], type='http', website=True)
    @http.route(['/downloads/id'],  type='http', auth="public", methods=['GET', 'POST'], website=True)

    # @http.route(['//'], type='http', website=True)
    def preview_attachment_token_download(self, **post):
        #''' Descarga el archivo con el token '''
        # cr, uid, context = request.cr, request.uid, request.context
        # attachment = request.registry['ir.attachment']
        # attachment_id = attachment.search(
        #     cr, uid, [('token', '=', token)], limit=1)

        # if attachment_id:
        #     attachment_id = attachment_id[0]
        #     attachment = attachment.browse(cr, uid, attachment_id)
        #     # attachment.update_token() # genera nuevo token de seguridad
        # else:
        #     return http.local_redirect("/attachment/document_not_found/")
        
        #attachment_id=12
        return http.local_redirect("/web/binary/saveas?model=website&field=datas&filename_field=name&id=%s" % attachment_id)
        #return http.local_redirect("/web/login")



    @http.route(['/page/requimision'], auth='public', website=True)
    def index(self, **kw):
        files = http.request.env['website.archive'].sudo()
        return http.request.render('donacion.mision', {
            'files': files.search([]),
        })



    @http.route(['/controller/url/path'], auth='public', website=True)
    def download_pdf_method(self,model,field,id,file_name=None,**kwargs):

        #Model = request.env['website.archive'].sudo().search([('id', '=',int(id))])
        Model = request.env['website.archive'].sudo().search([('file_name', '=',file_name)])

        filecontent = base64.b64decode(Model.file or '')
        headers = werkzeug.datastructures.Headers()

        #return request.make_response(filecontent)
        #pdb.set_trace()

        if not filecontent:
            return request.not_found()
        else:
            if not file_name:
                filename = '%s_%s' % (model.replace('.', '_'), id)
                headers.add('Content-Disposition', 'attachment', filename=filename)
                return request.make_response(filecontent,headers)
            else:
                headers.add('Content-Disposition', 'attachment', filename=file_name)
                return request.make_response(filecontent,headers)

        #return http.local_redirect("/web/binary/saveas?model=website&field=datas&filename_field=name&id=%s" % attachment_id)
        
        #return http.request.env['website.archive']._csv_download({'id': 1})
        #return file


    # @http.route('/csv/download/<int:rec_id>/', auth='user', website=True)
    # def csvdownload(self, rec_id, **kw):

    #     pdb.set_trace()                


    #     return http.request.env['website.archive']._csv_download({'rec_id': rec_id})