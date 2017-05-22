# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo import http
from odoo.http import request# -*- coding: utf-8 -*-
# import psycopg2
# from odoo import tools
# from odoo.addons.base.ir.ir_mail_server import MailDeliveryException
# from odoo.tools.safe_eval import safe_eval
# _logger = logging.getLogger(__name__)
import datetime
from odoo.exceptions import UserError, except_orm, Warning, RedirectWarning
import smtplib


from pprint import pprint
import pdb



def ref_xml_id(self_odoo, module, xml_id):
    domain = [('module', '=', module), ('name', '=', xml_id)]
    res = self_odoo.sudo().env['ir.model.data'].search(domain)
    return self_odoo.sudo().env[res.model].browse(res.res_id)


#ESTE ES LA FUNCION QUE GENERA EL NUMERO DE EXPEDIENTE QUE SE GENERA CUANDO REGISTRA DE ACUERDO AL PROCESO DONACION O MISION
def numero_exp(self,proceso):
   #aca se genera un numero de expediente 
    x = datetime.datetime.now()
    anio=x.year
    str_anio=str(anio)
    digito_anio=str_anio[-2:]

    #Llama al id de la donacion
    id_donacion=self.id
    identificador=str(id_donacion)

    if proceso=='D':
     
        #consulta de que donatario es la donacion
        query_user='SELECT create_uid FROM donacion_requisito WHERE id=%s' % id_donacion
        self.env.cr.execute(query_user)    
        user=self.env.cr.fetchone()[0]  
     
        #cuenta cuantos registros tiene en donacion_requisito de cada usuario    
        query='SELECT count(*) FROM donacion_requisito WHERE create_uid=%s' % user
        self.env.cr.execute(query)
        cantidad_registros=self.env.cr.fetchone()[0]
        numero_tres=str(cantidad_registros)
        longitud=len(numero_tres)
        if longitud==1:
            digito_tres='00'+numero_tres       
        elif longitud==2:
            digito_tres='0'+numero_tres
        elif longitud==3:
            digito_tres=numero_tres
        else:
            raise UserError("excede las 3 cifras del formato establecido del codigo de tramite, comuniquese con el admin")
        
      
    else:
        
        #consulta de que donatario es la donacion
        query_user='SELECT create_uid FROM mision_requisito WHERE id=%s' % id_donacion
        self.env.cr.execute(query_user)    
        user=self.env.cr.fetchone()[0]  
     
        #cuenta cuantos registros tiene en donacion_requisito de cada usuario    
        query='SELECT count(*) FROM mision_requisito WHERE create_uid=%s' % user
        self.env.cr.execute(query)
        cantidad_registros=self.env.cr.fetchone()[0]
        numero_tres=str(cantidad_registros)
        longitud=len(numero_tres)
        if longitud==1:
            digito_tres='00'+numero_tres       
        elif longitud==2:
            digito_tres='0'+numero_tres
        elif longitud==3:
            digito_tres=numero_tres
        else:
            raise UserError("excede las 3 cifras del formato establecido del codigo de tramite, comuniquese con el admin")
        
      

    #genera un numero de acuerdo al id de la donacion que se insertara en el segundo parte del tramite
    if len(identificador) == 1:
        digito_seis='00000'+identificador

    elif len(identificador) == 2:
        digito_seis='0000'+identificador

    elif len(identificador) == 3:
        digito_seis='000'+identificador
      
    elif len(identificador) == 4:
        digito_seis='00'+identificador

    elif len(identificador) == 5:
        digito_seis='0'+identificador

    elif len(identificador) == 6:
        digito_seis=identificador
    else:
        raise UserError("excede las 6 cifras de formato establecido del codigo de tramite, comuniquese con el admin")

    #Aca se arma el numero de expediente de acuerdo a variables arriba generadas de acuerdo al formato
    numero_expediente_digital=digito_anio+'-'+digito_seis+'-'+digito_tres+'-'+proceso
    
    return numero_expediente_digital


class rols(models.Model):
    _name='donacion.roles'
    name=fields.Char('Nombre del rol')


class Partner(models.Model):
    _inherit = 'res.partner'
   
    dni_person=fields.Char('DNI persona')
    encargado_1= fields.Char('Persona encargada')
    institucion= fields.Char('Institucion')
    direccioninstitucion= fields.Char('Direccion de la institucion')

    docautoriza= fields.Binary('Adjuntar docautoriza', required=True) 
    descripcion= fields.Char('Descripcion de la Institucion')
    #documento_apci= fields.Binary('Adjuntar documento de apci', required=True)
    #name_apci= fields.Char('Nom de apci')

    #documento_entidades= fields.Binary('Adjuntar documento de entidades enumeradas', required=True)
    #name_entidades = fields.Char('Nombre de documento de entidades')

class Users(models.Model):
    _inherit = 'res.users'

    partner_id = fields.Many2one('res.partner','partner')
    rol_id = fields.Many2one('donacion.roles','rol')
    comment=fields.Text('Comentario')

    documentaut= fields.Binary('Documento de autorizacion',attachment=True)
    name_filename = fields.Char('nombre del archivo')

    doc_apci=fields.Binary('Documento de APCI')
    name_apci=fields.Char('Nombre de documento de autorizacion')

    doc_entidades=fields.Binary('Documento de entidades')
    name_entidades=fields.Char('Entidades')

    encargado_1 = fields.Char(string='Encargado',store=True,related='partner_id.encargado_1')
    dni_person = fields.Char(string='DNI',store=True,related='partner_id.dni_person')
    institucion = fields.Char(string='Institucion',store=True,related='partner_id.institucion')
    direccioninstitucion = fields.Char(string='Direccion institucion',store=True,related='partner_id.direccioninstitucion')
    observacion = fields.Char('Description')  
    email_remitente=fields.Char(compute='_compute_remitente')
    organizacion = fields.Char('organizacion', default='M')


class Usuario_solicitud(models.Model):
    #_inherit = 'res.users'
    _name='donacion.usuario'
    name=fields.Char('nombre')
    login=fields.Char('login')
    password=fields.Char('password')
    company_id=fields.Integer('compania')
    partner_id = fields.Many2one('res.partner','partner')
    rol_id = fields.Many2one('donacion.roles','rol')
    comment=fields.Text('Comentario')

    documentaut= fields.Binary('Documento de autorizacion',attachment=True)
    name_filename = fields.Char('nombre del archivo')

    doc_apci=fields.Binary('Documento de APCI')
    name_apci=fields.Char('Nombre de documento de autorizacion')

    doc_entidades=fields.Binary('Documento de entidades')
    name_entidades=fields.Char('Entidades')

    encargado_1 = fields.Char(string='Encargado',store=True,related='partner_id.encargado_1')
    dni_person = fields.Char(string='DNI',store=True,related='partner_id.dni_person')
    institucion = fields.Char(string='Institucion',store=True,related='partner_id.institucion')
    direccioninstitucion = fields.Char(string='Direccion institucion',store=True,related='partner_id.direccioninstitucion')
    observacion = fields.Char('Description')  
    email_remitente=fields.Char(compute='_compute_remitente')
    organizacion = fields.Char('organizacion', default='M')

    @api.multi
    def _compute_remitente(self):
        cont=[]

        for record in self:

            OGCTI=self.env['res.users'].search([('rol_id','in','OGCTI')])

            for x in OGCTI:
                user=self.env['res.users'].browse(x.id) 

                email=user.partner_id.email
                cont.append(email)
         
            correos=','.join(cont)

            print(correos)
            #pdb.set_trace()
        
        record.email_remitente = correos


    @api.one
    def toggle_active(self):     
           
        self.active = not self.active
  
        if self.active==True:

            template = self.env.ref('auth_signup.set_password_email')            

            print(self.id)
            pdb.set_trace()

            self.env['mail.template'].sudo().browse(template.id).send_mail(71,force_send=True)

        return True

    # @api.model
    # def create(self,values):
      
    #     return super(Users, self).create(values)

    @api.model
    def get_or_create_user(self, login,  documento,name_filename, perfil={}, email=None, dict_partner=None):
        dict_partner = dict_partner or {}

        odoo_user = self.sudo().search([('active', '=', True), ('login', '=', login)])
    
        
        if odoo_user:
            print('existe usuario') 
            #return {'value':{},'warning':{'title':'warning','message':'Your message'}}
        else:            

            print('no existe usuario')           
            #pdb.set_trace()
            res_partner = http.request.env['res.partner']
            #res_users = http.request.env['res.users']
            res_users = http.request.env['donacion.usuario']
           
            #values = dict_partner
            #print(values)
            #partner = res_partner.sudo().create(values)
            donatario = self.env['donacion.roles'].sudo().search([('name', '=',  'DONATARIO')])

            print(donatario)  

            dict_users=dict(
                login=login,
                password=login,
                company_id=1,
                documentaut=documento,
                name_filename=name_filename,
                #estos datos son de partner
                name=dict_partner.get('name'),   
                email=dict_partner.get('email'),
                docautoriza=dict_partner.get('docautoriza'),                
                organizacion=dict_partner.get('tipo'),
                active=False,                
                mobile=dict_partner.get('mobile'),
                phone=dict_partner.get('phone'),
                encargado_1=dict_partner.get('persona'),
                dni_person=dict_partner.get('dni'),
                institucion=dict_partner.get('institucion'),
                doc_apci=dict_partner.get('documento_apci'),
                #documento_apci=dict_partner.get('documento_apci'),
                name_apci=dict_partner.get('name_apci'),
                doc_entidades= dict_partner.get('documento_entidades'),
                name_entidades=dict_partner.get('name_entidades'),
                direccioninstitucion=dict_partner.get('direccioninstitucion'),
                street=dict_partner.get('direccionpersonal'),
                rol_id=donatario.id
            )

          
            #users = self.sudo().create(dict_users)
            users = self.sudo().with_context(no_reset_password=True).create(dict_users)

            group_donacion_requisito_donatario = ref_xml_id(self, 'donacion', 'group_donacion_requisito_donatario')
            group_website=ref_xml_id(self,'website','group_website_designer')
            group_site_web=ref_xml_id(self,'website','group_website_publisher')

            print(group_donacion_requisito_donatario)
            print(group_website)
            print(group_site_web)
            #pdb.set_trace()

            # group_donacion_requisito_donatario.write({'users': [[6, False, list(set([u.id for u in group_donacion_requisito_donatario.users + users]))]]})
            # group_website.write({'users': [[5, True, list(set([u.id for u in group_website.users + users]))]]})
            # group_site_web.write({'users': [[5, True, list(set([u.id for u in group_site_web.users + users]))]]})
           

            # if users:
            #     template = self.env.ref('donacion.email_newuser_ogcti')              
            #     self.env['mail.template'].sudo().browse(template.id).send_mail(users.id,force_send=True)

        return users.id
        #return {'users':users.id,'warning':{'title':'warning','message':'Your message'}}



class donacion(models.Model):

    _inherit =['mail.thread', 'ir.needaction_mixin']
    _name = 'donacion.requisito'

    name = fields.Char('Nombre del Donante', required=True)
    descripcion = fields.Text('Descripcion de la donacion', required=True)
    #is_done = fields.Boolean('Done?')
    active = fields.Boolean('Active', default=True)
    numero_expediente=fields.Char('Numero de expediente',attachment=True)
    
    solicitud= fields.Binary('Adjuntar Solicitud de emisión de Resolución de Aceptación de donaciones proveniente del exterior dirigido a OGCTI',attachment=True)
    name_filename_solicitud=fields.Char('Nombre de la solicitud')

    opinion_tecnica= fields.Binary('Adjuntar Solicitud de emisión de opinión técnica,',attachment=True)
    name_filename_tecnico=fields.Char('Nombre de la solicitud de emisión de opinión técnica')

    carta= fields.Binary('Adjuntar Carta de donacion de la Entidad donante',attachment=True)
    name_filename_carta=fields.Char('Nombre de la carta de donacion de la Entidad donante')
   
    embarque= fields.Binary('Adjuntar copia simple del documento de transporte',attachment=True)
    name_filename_embarque=fields.Char('Nombre copia simple del documento de transporte')
    #lista= fields.Binary('Adjuntar lista', required=True)


    validar_tecnico=fields.Boolean('Validar solicitud de emisión de opinión técnica', default=False)
    validar_solicitud=fields.Boolean('Validar solicitud de la OGCTI', default=False)
    validar_carta=fields.Boolean('validar carta', default=False)
    validar_embarque=fields.Boolean('validar embarque', default=False)

    state = fields.Selection([ ('B', 'Borrador'), 
                               ('I', 'Iniciado'),                                                          
                               ('R', 'Registrado'),
                               ('V', 'Validado'),
                               #('A', 'Aprobado'),
                               ('01', 'observado por OGCTI'),
                               ('02', 'observado por DIGEMID/DIGESA')                        
                               #('C', 'Cerrado')
                              ],
                              string='Estado', default='B',track_visibility="onchange")

    # track_visibility="onchange" 
    lista_ids=fields.One2many('donacion.lista','donacion_id','Lista')
    observacion_ogcai=fields.Text('Observacion OGCTI', translate=True)
    observacion_digesa=fields.Text('Observacion  DIGESA', translate=True)
    observacion_digemid=fields.Text('Observacion DIGEMID', translate=True)
    
    informedigesa= fields.Binary('Adjuntar informe tecnico digesa',store=True,attachment=True)
    name_filename_digesa = fields.Char('Nombre del informe digesa')
    informedigemid= fields.Binary('Adjuntar informe tecnico digemid',store=True,attachment=True)
    name_filename_digemid = fields.Char('Nombre del informe digemid')
    #validar Digesa-Digemid
    vdigesa= fields.Boolean('Visto Bueno DIGESA',default=False)
    vdigemid= fields.Boolean('Visto Bueno DIGEMID',default=False)

    enviar_digesa= fields.Boolean('DIGESA',default=False)
    enviar_digemid= fields.Boolean('DIGEMID',default=False)

    email_from=fields.Char(compute='_compute_from')
    email_from_name=fields.Char(compute='_compute_from_name')
    email_to=fields.Char(compute='_compute_email')

    user_id_org = fields.Char(string='Organizacion',related='create_uid.organizacion')

    @api.multi
    def _compute_from_name(self):
        for record in self:

            em=self.env.uid
            user=self.env['res.users'].browse(em)
            emailfromname=user.name

            record.email_from_name=emailfromname

    @api.multi
    def _compute_from(self):
        for record in self:

            em=self.env.uid
            user=self.env['res.users'].browse(em)
            emailfrom=user.partner_id.email             

            record.email_from=emailfrom
 
    @api.depends('enviar_digesa','enviar_digemid','state','vdigesa','vdigemid')
    def _compute_email(self):
        for record in self:
            depend=()
            cont=[]

   
            if record.state=='01' or record.state=='V':
                #depend=depend+('DONATARIO',)          
                donatario=self.browse(self.id)           
                correos=donatario.create_uid.email

            else:
                if record.state=='I':
                
                    depend=depend+('OGCTI',)                
                 
                else:
                    if record.state=='R':
                        if record.vdigesa==False and record.vdigemid==False:
                            if record.enviar_digesa:
                                depend=depend+('DIGESA',)                   

                            if record.enviar_digemid:
                                depend=depend+('DIGEMID',)
                        else:
                            
                            if record.vdigesa==True or record.vdigemid==True:
                                donatario=self.browse(self.id)           
                                donatariocorreo=donatario.create_uid.email
                                cont.append(donatariocorreo)
                                depend=depend+('OGCTI',)                


                OGCTI=self.env['res.users'].search([('rol_id','in',depend)])

                for x in OGCTI:
                    user=self.env['res.users'].browse(x.id) 

                    email=user.partner_id.email
                    cont.append(email)
         
                correos=','.join(cont)    
           

        record.email_to = correos


    #ACA LAS ACCIONES DEL WORKFLOW FLUJO NORMAL
    @api.model
    def action_borrador(self):    
        
        registrado=self
        registrado.write({'state':'B'})
        return True

    @api.model
    def action_iniciado(self): 
        registrado=self
        registrado.write({'state':'I'})
        self.send_mail_template()
     
        return True   

    @api.model
    def action_registrado(self):

        registrado=self
        proceso='D'
        ne=numero_exp(self,proceso)
        registrado.write({'state':'R','numero_expediente':ne})
        self.send_mail_template()        

        return True

    @api.model
    def action_validado(self):         
        registrado=self
        registrado.write({'state':'V'})
        self.send_mail_template()        

        return True


    @api.model
    def action_observado1(self): 
        print('observado1')        
        registrado=self
        registrado.write({'state':'01'})

        self.send_mail_template()   
        return True

    @api.model
    def action_observado2(self):       
        registrado=self
        registrado.write({'state':'02'})
        return True


    #FUNCIONES DE BOTON A DIGESA - DIGEMID
    @api.one
    def visto_digesa(self):     
        self.vdigesa = not self.vdigesa
        #if self.vdigesa==True:
          
        self.send_mail_template()
        return True
  
    @api.one
    def visto_digemid(self):     
        self.vdigemid = not self.vdigemid
        #if self.vdigemid==True:
            
        self.send_mail_template()
        return True

    # @api.one
    # def enviado_digesa(self):     
    #     self.enviar_digesa = not self.enviar_digesa
    #     return True

    # @api.one
    # def enviado_digemid(self):     
    #     self.enviar_digemid = not self.enviar_digemid        
    #     return True


    @api.multi
    def send_mail_template(self):       

        template = self.env.ref('donacion.email_template_demo')       
        return self.env['mail.template'].browse(template.id).send_mail(self.id,force_send=True)



class lista(models.Model):
    _name='donacion.lista'
    name = fields.Char('Nombre de marca', required=True)    
    name_generico = fields.Char('DCI ó nombre genérico')    
    #name_generico = fields.Many2one('linea',string="DCI ó nombre genérico")
    concentracion = fields.Char('Concentración')
    forma = fields.Char('Forma farmacéutica')
    lote = fields.Char('Lote')
    fecha_vencimiento = fields.Datetime('Fecha de vencimiento')
    temperatura = fields.Char('T° de almacenamiento')
    pais = fields.Many2one('res.country','Nombre y País del laboratorio fabricante')
    
    # certificado_protocolo = fields.Char('Certificado y Protocolo de análisis en el caso de productos biológicos')
    # certificado_negatividad = fields.Char('Certificado de negatividad del VIH, Hepatitis B y C, Encefalopatía espongiforme bovina en el caso de Hemoderivados')
    # certificado_exportacion = fields.Char('Certificado de Exportación emitido por la autoridad nacional del país de donde proviene la donación, en el caso de productos estupefacientes, psicotrópicos sujetos a fiscalización sanitaria')

    certificado_protocolo= fields.Binary('Certificado y Protocolo de análisis en el caso de productos biológicos',store=True,attachment=True)
    certificado_negatividad= fields.Binary('Certificado de negatividad del VIH, Hepatitis B y C, Encefalopatía espongiforme bovina en el caso de Hemoderivados',store=True,attachment=True)
    certificado_exportacion= fields.Binary('Certificado de Exportación emitido por la autoridad nacional del país de donde proviene la donación, en el caso de productos estupefacientes, psicotrópicos sujetos a fiscalización sanitaria',store=True,attachment=True)

    cantidad=fields.Integer('Cantidad')
    donacion_id=fields.Many2one('donacion.requisito','donacion')
    mision_id=fields.Many2one('mision.requisito','Mision')
    categoria=fields.Many2one('donacion.categoria','Categoria')
    aprobacion=fields.Boolean('Aprobacion de item',default=False)
    aprove=fields.Many2many('donacion.lista.verificacion','verifcar')

# class lista_verificacion(models.Model):
#     _name='donacion.lista.verificacion'
#     lista_id=fields.Many2one('donacion.lista')
#     verificacion= fields.Boolean('Verificar el estado',default=False)



class categoria(models.Model):
    _name='donacion.categoria'
    name=fields.Char('Nombre',required=True)


# class proceso(models.Model):
#     _name='donacion.proceso'
#     name = fields.Char('Nombre del proceso', required=True)
#     codigo = fields.Char('Codigo del proceso', required=True)


class mision(models.Model):
    _name='mision.requisito'
    name = fields.Char('Nombre', required=True)
    descripcion=fields.Char('Descripcion', required=True)
    fecha=fields.Datetime('Ingrese la fecha de la Mision')
    carta_ogcai= fields.Binary('Carta dirigida al director ogcai') 
    plan_trabajo= fields.Binary('Plan de trabajo de las actividades con cronograma') 
    listaprofesionales_ids=fields.One2many('mision.listaprofesionales','mision_id','Lista Profesionales')
    declaracion_jurada= fields.Binary('Declaracion jurada de no tener pendiente entrega de informes de actividades sanitarias realizadas en el pais') 
    carta_organizadora= fields.Binary('Carta de compromiso  de la institucion organizadora nacional o la institucion extranjera responsable del seguimiento posterior a las atenciones segun corresponda') 
    carta_donacion= fields.Binary('Carta de donacion indicando el monto total y el beneficiario') 
    lista_donacion_mision= fields.Binary('Listado detallado de bienes a ser donados') 
    lista_donacion_temporal= fields.Binary('Listado detallado de bienes en calidad de ingreso temporal') 
    carta_embajada_consulado= fields.Binary('Carta presentada en la embajada o consulado del peru en el pais de origen sobre la mision sanitaria') 
    itinerario_vuelo= fields.Binary('Itinerario de vuelo arribo y salida del pais de los profesionales que traen la donacion o ingreso temporal') 
    state = fields.Selection([ ('B', 'Borrador'), 
                               ('I', 'Iniciado'),                                                          
                               ('R', 'Registrado'),
                               ('V', 'Validado'),
                               #('A', 'Aprobado'),
                               ('01', 'observado por OGCTI'),
                               ('02', 'observado por DISA/DIRESA')                        
                               #('C', 'Cerrado')
                              ],
                              string='Estado', default='B')

    enviar_disa= fields.Boolean('DISA',default=False)
    enviar_diresa= fields.Boolean('DIRESA',default=False)
    numero_expediente=fields.Char('Numero de expediente mision',attachment=True)

    email_from=fields.Char(compute='_compute_from')
    email_from_name=fields.Char(compute='_compute_from_name')
    email_to=fields.Char(compute='_compute_email')

    vdisa= fields.Boolean('Visto Bueno DISA',default=False)
    vdiresa= fields.Boolean('Visto Bueno DIRESA',default=False)
    observacion_ogcti=fields.Text('Observacion OGCTI', translate=True)
    observacion_disa=fields.Text('Observacion  DISA', translate=True)
    observacion_diresa=fields.Text('Observacion DIRESA', translate=True)
    
    informedisa= fields.Binary('Adjuntar informe tecnico disa',store=True,attachment=True)
    name_filename_disa = fields.Char('Nombre del informe disa')
    informediresa= fields.Binary('Adjuntar informe tecnico diresa',store=True,attachment=True)
    name_filename_diresa = fields.Char('Nombre del informe diresa')
   
    @api.multi
    def _compute_from_name(self):
        for record in self:

            em=self.env.uid
            user=self.env['res.users'].browse(em)
            emailfromname=user.name

            record.email_from_name=emailfromname

    @api.multi
    def _compute_from(self):
        for record in self:

            em=self.env.uid
            user=self.env['res.users'].browse(em)
            emailfrom=user.partner_id.email             

            record.email_from=emailfrom

    @api.depends('enviar_disa','enviar_diresa','state','vdiresa','vdisa')
    def _compute_email(self):
        for record in self:
            depend=()
            cont=[]

            if record.state=='01' or record.state=='V':
                #depend=depend+('DONATARIO',)          
                donatario=self.browse(self.id)           
                correos=donatario.create_uid.email

            else:
                if record.state=='I':
                
                    depend=depend+('OGCTI',)                
                 
                else:
                    if record.state=='R':
                        if record.vdisa==False and record.vdiresa==False:
                            if record.enviar_disa:
                                depend=depend+('DISA',)                   

                            if record.enviar_diresa:
                                depend=depend+('DIRESA',)
                        else:
                            
                            if record.vdisa==True or record.vdiresa==True:
                                donatario=self.browse(self.id)           
                                donatariocorreo=donatario.create_uid.email
                                cont.append(donatariocorreo)
                                depend=depend+('OGCTI',)                


                OGCTI=self.env['res.users'].search([('rol_id','in',depend)])
                
                for x in OGCTI:
                    
                    user=self.env['res.users'].browse(x.id) 

                    print(user)

                    email=user.partner_id.email
                    cont.append(email)
         
                correos=','.join(cont)

                print('correos')    
                print(correos)    
           
                #pdb.set_trace()

        record.email_to = correos


    #ACA LAS ACCIONES DEL WORKFLOW FLUJO NORMAL
    @api.model
    def action_borrador(self):
        print('csf llego hasta aki la ')
        mision=self
        mision.write({'state':'B'})
        return True

    @api.model
    def action_iniciado(self):        
        #pdb.set_trace()
        mision=self
        mision.write({'state':'I'})
        self.send_mail_template_m()     
        return True   

    @api.model
    def action_registrado(self):
        mision=self  
        proceso='M'
        ne=numero_exp(self,proceso)
        mision.write({'state':'R','numero_expediente':ne})
        self.send_mail_template_m()
        return True


    @api.model
    def action_validado(self):         
        mision=self
        mision.write({'state':'V'})
        
        self.send_mail_template_m()        

        return True

    @api.model
    def action_observado1(self): 
        print('observado1')        
        mision=self
        mision.write({'state':'01'})

        self.send_mail_template_m()   
        return True

    @api.one
    def visto_disa(self):     
        
        self.vdisa = not self.vdisa

        #if self.vdisa==True:
            
        self.send_mail_template_m()

        return True

    @api.one
    def visto_diresa(self): 


        self.vdiresa = not self.vdiresa
   

        #if self.vdiresa==True:
            
        self.send_mail_template_m()
           
        return True

    @api.multi
    def send_mail_template_m(self):  
        template = self.env.ref('donacion.email_template_mision')       
        return self.env['mail.template'].browse(template.id).send_mail(self.id,force_send=True)


class listaprofesionales(models.Model):
    _name='mision.listaprofesionales'
    name = fields.Char('Nombre', required=True)
    institucion=fields.Char('Institucion')
    pais=fields.Char('Pais de procedencia')
    especialidad=fields.Char('Especialidad')
    pasaporte= fields.Binary('Fotocopia simple de Pasaporte') 
    titulo= fields.Binary('Fotocopia simple de Titulo Profesional') 
    licencia= fields.Binary('Fotocopia simple de licencia para ejercer su profesion en su pais') 
    cv= fields.Binary('Curriculum Vitae')
    mision_id=fields.Many2one('mision.requisito','misiones')

