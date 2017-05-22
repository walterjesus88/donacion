# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo import http
from odoo.http import request
# import psycopg2

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


class Rols(models.Model):
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
    disa_diresa=fields.Boolean('Flat Diresas', default=False)
    #categoria_profesional=fields.Many2one('mision.categoriaprofesional','categoria profesional')

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
        
        record.email_remitente = correos


    @api.one
    def toggle_active(self):
        self.active = not self.active  
        if self.active==True:
            #template = self.env.ref('auth_signup.reset_password_email')            
            template = self.env.ref('donacion.example_email_template')

            self.env['mail.template'].sudo().browse(template.id).send_mail(self.id,force_send=True)

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
            res_partner = http.request.env['res.partner']
            res_users = http.request.env['res.users']       
            #partner = res_partner.sudo().create(values)
            donatario = self.env['donacion.roles'].sudo().search([('name', '=', 'DONATARIO')])

            dict_users=dict(
                login=login,
                password=login,
                company_id=1,
                documentaut=documento,
                name_filename=name_filename,
                rol_id=donatario.id,
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
                street=dict_partner.get('direccionpersonal')
            )          
            #users = self.sudo().create(dict_users)
            users = self.sudo().with_context(no_reset_password=True).create(dict_users)
            
            group_donacion_requisito_donatario = ref_xml_id(self, 'donacion', 'group_donacion_requisito_donatario')
            group_website=ref_xml_id(self,'website','group_website_designer')
            group_site_web=ref_xml_id(self,'website','group_website_publisher')
            group_minsa=ref_xml_id(self,'donacion','group_donacion_minsa')
            group_ong=ref_xml_id(self,'donacion','group_donacion_ong')
            group_employee=ref_xml_id(self,'base','group_user')


            if dict_partner.get('tipo')=='M':
                group_minsa.write({'users': [[6, False, list(set([u.id for u in group_minsa.users + users]))]]})
            else:
                group_ong.write({'users': [[6, False, list(set([u.id for u in group_ong.users + users]))]]})
          
            group_donacion_requisito_donatario.write({'users': [[6, False, list(set([u.id for u in group_donacion_requisito_donatario.users + users]))]]})
            group_website.write({'users': [[5, True, list(set([u.id for u in group_website.users + users]))]]})
            group_site_web.write({'users': [[5, True, list(set([u.id for u in group_site_web.users + users]))]]})      

            if users:
                template = self.env.ref('donacion.email_newuser_ogcti')              
                self.env['mail.template'].sudo().browse(template.id).send_mail(users.id,force_send=True)

        return users.id

class Categoria(models.Model):
    #categoria de donaciones
    _name='donacion.categoria'
    name=fields.Char('Nombre',required=True)

class Dispositivosmedicos(models.Model):
    _name='donacion.dispositivos.medicos'

    name=fields.Char('Denominación o nombre común, generico o universal',required=True)
    cantidad=fields.Integer('Cantidad unidades')
    codigo=fields.Char('Codigo, marca y modelo')
    lote_serie=fields.Integer('Numero de lote y/o serie')
    fecha_expiracion=fields.Datetime('Fecha de expiracion y/o vencimiento/Fecha de fabricacion')
    finalidad_uso=fields.Char('Finalidad de uso o uso previsto por el fabricante')
    forma_presentacion=fields.Char('Forma de presentacion o comercial')
    accesorios=fields.Char('Accesorios')
    componentes=fields.Char('componentes de la forma de presentacion o comercial')
    condiciones=fields.Char('Condiciones especiales de almacenamiento y/o conservacion')
    certificado_repotenciacion=fields.Binary('Certificado de repotenciacion',store=True,attachment=True)
    certificado_operatividad=fields.Binary('Constancia o certificado de operatividad',store=True,attachment=True)
    manual_operacion=fields.Binary('Manual de operacion o usuario o instrucciones',store=True,attachment=True)
    dispositivo_id=fields.Many2one('donacion.requisito','donacion')

class Productossanitarios(models.Model):
    _name='donacion.productos.sanitarios'
    name=fields.Char('Nombre del producto',required=True)
    cantidad=fields.Integer('Cantidad (unidades)')
    lote_serie=fields.Char('Numero de lote y/o serie')
    fecha_vencimiento=fields.Datetime('Fecha de Vnecimiento')
    etiquetado=fields.Binary('Etiquetado con informacion solicitada',store=True,attachment=True)
    condiciones=fields.Char('Condiciones especiales de conservacion')
    productosanitario_id=fields.Many2one('donacion.requisito','donacion')

class Donacion(models.Model):

    _inherit =['mail.thread', 'ir.needaction_mixin']
    _name = 'donacion.requisito'

    user_id = fields.Many2one('res.users','users')
    name = fields.Char('Titulo de la donación', required=True)
    descripcion = fields.Char('Nombre del Donante')
    #is_done = fields.Boolean('Done?')
    active = fields.Boolean('Active', default=True)
    numero_expediente=fields.Char('Número de expediente',attachment=True)    
    
    solicitud= fields.Binary('Solicitud de emisión de Resolución de Aceptación de donaciones proveniente del exterior dirigido a OGCTI',attachment=True)
    name_filename_solicitud=fields.Char('Nombre de la solicitud')
    comentario_solicitud=fields.Char('Comentario solicitud')    
    opinion_tecnica= fields.Binary('Solicitud de emisión de opinión técnica ',attachment=True)
    name_filename_tecnico=fields.Char('Nombre de la solicitud de emisión de opinión técnica')
    comentario_opinion_tecnica=fields.Char('Comentario opinion tecnica')
    carta= fields.Binary('Carta de donacion de la Entidad donante',attachment=True,required=True)    
    name_filename_carta=fields.Char('Nombre de la carta de donacion de la Entidad donante')
    comentario_carta=fields.Char('Comentario carta donacion')
    embarque= fields.Binary('Copia simple del documento de transporte',attachment=True,required=True)
    name_filename_embarque=fields.Char('Nombre copia simple del documento de transporte')
    comentario_embarque=fields.Char('Comentario embarque')
    #adicional archivos
    instrumentos_medicos=fields.Binary('Instrumentos médicos',store=True,attachment=True)
    name_filename_instrumentos_medicos=fields.Char('Nombre Instrumentos medicos')
    alimentos=fields.Binary('Alimentos',store=True,attachment=True)
    name_filename_alimentos=fields.Char('Nombre Alimentos')
    utiles_escolares=fields.Binary('Utiles escolares',store=True,attachment=True)
    name_filename_utiles_escolares=fields.Char('Nombre Utiles escolares')
    productos_higiene=fields.Binary('Productos de higiene personal',store=True,attachment=True)
    name_filename_productos_higiene=fields.Char('Nombre Productos de higiene personal')
    equipos_medicos=fields.Binary('Equipos Médicos',store=True,attachment=True)
    name_filename_equipos_medicos=fields.Char('Nombre Equipos Médicos')
    validar_tecnico=fields.Boolean('Validar', default=False)
    validar_solicitud=fields.Boolean('Validar' , default=False)
    validar_carta=fields.Boolean('validar ', default=False)
    validar_embarque=fields.Boolean('validar ', default=False)
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
    lista_ids=fields.One2many('donacion.lista','donacion_id','Lista')
    dispositivos_ids=fields.One2many('donacion.dispositivos.medicos','dispositivo_id','Dispositivos medicos')
    prodsanitarios_ids=fields.One2many('donacion.productos.sanitarios','productosanitario_id','Productos Sanitarios')
    observacion_ogcai=fields.Text('Observacion OGCTI', translate=True)
    observacion_digesa=fields.Text('Observacion  DIGESA', translate=True)
    observacion_digemid=fields.Text('Observacion DIGEMID', translate=True)    
    informedigesa= fields.Binary('Adjuntar informe tecnico digesa',store=True,attachment=True)
    name_filename_digesa = fields.Char('Nombre del informe digesa')
    informedigemid= fields.Binary('Adjuntar informe tecnico digemid',store=True,attachment=True)
    name_filename_digemid = fields.Char('Nombre del informe digemid')
    vdigesa= fields.Boolean('Visto Bueno DIGESA',default=False)
    vdigemid= fields.Boolean('Visto Bueno DIGEMID',default=False)
    enviar_digesa= fields.Boolean('DIGESA',default=False)
    enviar_digemid= fields.Boolean('DIGEMID',default=False)
    email_from=fields.Char(compute='_compute_from')
    email_from_name=fields.Char(compute='_compute_from_name')
    email_to=fields.Char(compute='_compute_email')
    user_id_organ = fields.Char(string='Organizacion',readonly=True,related='create_uid.organizacion')
    categoria_ids=fields.Many2many('donacion.categoria','categorias')

    @api.multi
    def _compute_from_organizacion(self):
        for record in self:

            em=self.env.uid
            user=self.env['res.users'].browse(em)
            organizacion=user.organizacion
            record.user_categ=organizacion


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
                donatario=self.browse(self.id)           
                correos=donatario.create_uid.email

            else:
                if record.state=='I': 
                    group_ogcti=ref_xml_id(self,'donacion','group_donacion_requisito_ogcai')
                    depend=depend+(group_ogcti,) 
                 
                else:
                    if record.state=='R':
                        if record.vdigesa==False and record.vdigemid==False:
                            if record.enviar_digesa:                            
                                group_digesa=ref_xml_id(self,'donacion','group_donacion_requisito_digesa')
                                depend=depend+(group_digesa,)

                            if record.enviar_digemid:                              
                                group_digemid=ref_xml_id(self,'donacion','group_donacion_requisito_digemid')
                                depend=depend+(group_digemid,)

                        else:                            
                            if record.vdigesa==True or record.vdigemid==True:
                                donatario=self.browse(self.id)           
                                donatariocorreo=donatario.create_uid.email
                                cont.append(donatariocorreo)
                                #depend=depend+('OGCTI',)   
                                group_ogcti=ref_xml_id(self,'donacion','group_donacion_requisito_ogcai')
                                depend=depend+(group_ogcti,)


                for group in depend:
                    OGCTI=self.env['res.groups'].browse(group.id).users
                   
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
        self.send_mail_template()
        return True
  
    @api.one
    def visto_digemid(self):     
        self.vdigemid = not self.vdigemid
        self.send_mail_template()
        return True

    @api.multi
    def send_mail_template(self): 
        template = self.env.ref('donacion.email_template_demo')       
        return self.env['mail.template'].browse(template.id).send_mail(self.id,force_send=True)

class Lista(models.Model):
    _name='donacion.lista'
    name = fields.Char('Nombre de marca', required=True)    
    name_generico = fields.Char('DCI ó nombre genérico')    
    concentracion = fields.Char('Concentración')
    forma = fields.Char('Forma farmacéutica')
    lote = fields.Char('Lote')
    fecha_vencimiento = fields.Datetime('Fecha de vencimiento')
    temperatura = fields.Char('T° de almacenamiento')
    pais = fields.Many2one('res.country','Nombre y País del laboratorio fabricante')
    certificado_protocolo= fields.Binary('Certificado y Protocolo de análisis en el caso de productos biológicos',store=True,attachment=True)
    certificado_negatividad= fields.Binary('Certificado de negatividad del VIH, Hepatitis B y C, Encefalopatía espongiforme bovina en el caso de Hemoderivados',store=True,attachment=True)
    certificado_exportacion= fields.Binary('Certificado de Exportación emitido por la autoridad nacional del país de donde proviene la donación, en el caso de productos estupefacientes, psicotrópicos sujetos a fiscalización sanitaria',store=True,attachment=True)
    cantidad=fields.Integer('Cantidad')
    donacion_id=fields.Many2one('donacion.requisito','donacion')   
    #aprobacion=fields.Boolean('Aprobacion de item',default=False)

class Mision(models.Model):
    _inherit =['mail.thread', 'ir.needaction_mixin']
    _name='mision.requisito'
    name = fields.Char('Nombre de la Misión', required=True)
    descripcion=fields.Char('Descripción')
    #fecha=fields.Datetime('Ingrese la fecha de la Mision')   

    carta_ogcai= fields.Binary('Carta dirigida a la Director(a) General de Cooperacion Tecnica Internacional, presentada 30 días antes del inicio de la Misión Sanitaria') 
    name_filename_carta_ogcai=fields.Char('Nombre de la carta ogcai')
    plan_trabajo= fields.Binary('Plan de trabajo de las actividades a realizar, con el cronograma especifico por dia de la mision sanitaria',store=True,attachment=True) 
    name_filename_plan_trabajo=fields.Char('Nombre del plan de trabajo')
    declaracion_jurada= fields.Binary('Declaracion jurada de no tener pendiente entrega de informes de actividades sanitarias realizadas en el pais',store=True,attachment=True) 
    name_filename_declaracion_jurada=fields.Char('Nombre de la declaracion_jurada')
    carta_organizadora= fields.Binary('Carta de compromiso  de la institucion organizadora nacional o la institucion extranjera responsable del seguimiento posterior a las atenciones segun corresponda',store=True,attachment=True) 
    name_filename_carta_organizadora=fields.Char('Nombre de la carta organizadora')
    carta_donacion= fields.Binary('Carta de donacion indicando el monto total y el beneficiario',store=True,attachment=True) 
    name_filename_carta_donacion=fields.Char('Nombre de la carta donacion')
    lista_donacion_mision= fields.Binary('Listado detallado de bienes a ser donados',store=True,attachment=True)
    name_filename_lista_donacion_mision=fields.Char('Nombre de la lista donacion mision')
    lista_donacion_temporal= fields.Binary('Listado detallado de bienes en calidad de ingreso temporal',store=True,attachment=True) 
    name_filename_lista_donacion_temporal=fields.Char('Nombre de la lista donacion temporal')
    carta_embajada_consulado= fields.Binary('Carta presentada en la Embajada o Consulado del Perú en el pais de origen sobre la misión sanitaria',store=True,attachment=True) 
    name_filename_carta_embajada_consulado=fields.Char('Nombre de la carta embajada consulado')
    itinerario_vuelo= fields.Binary('Itinerario de vuelo arribo y salida del país de los profesionales que traen la donacion o ingreso temporal',store=True,attachment=True) 
    name_filename_itinerario_vuelo=fields.Char('Nombre de itinerario vuelo')   

    validar_carta_ogcai=fields.Boolean('Validar', default=False)
    validar_plan_trabajo=fields.Boolean('Validar' , default=False)
    validar_declaracion_jurada=fields.Boolean('validar ', default=False)
    validar_carta_organizadora=fields.Boolean('validar ', default=False)
    validar_carta_donacion=fields.Boolean('validar ', default=False)
    validar_lista_donacion_mision=fields.Boolean('validar ', default=False)
    validar_lista_donacion_temporal=fields.Boolean('validar ', default=False)
    validar_carta_embajada_consulado=fields.Boolean('validar ', default=False)
    validar_itinerario_vuelo=fields.Boolean('validar ', default=False)

    listaprofesionales_ids=fields.One2many('mision.listaprofesionales','mision_id','Lista Profesionales')
    fecha_inicio=fields.Datetime('Fecha de inicio de la mision sanitaria')
    fecha_fin=fields.Datetime('Fecha de inicio de la mision sanitaria')

    state = fields.Selection([ ('B', 'Borrador'), 
                               ('I', 'Iniciado'),                                                          
                               ('R', 'Registrado'),
                               ('V', 'Validado'),
                               #('A', 'Aprobado'),
                               ('01', 'observado por OGCTI'),
                               ('02', 'observado por DISA/DIRESA')                        
                               #('C', 'Cerrado')
                              ],
                              string='Estado', default='B',track_visibility="onchange")

    enviar_disa= fields.Boolean('DISA',default=False)
    enviar_diresa= fields.Boolean('DIRESA',default=False)
    numero_expediente=fields.Char('Número de expediente mision',attachment=True)
    email_from=fields.Char(compute='_compute_from')
    email_from_name=fields.Char(compute='_compute_from_name')
    email_to=fields.Char(compute='_compute_email')
    vdisa= fields.Boolean('Visto Bueno DISA',default=False)
    vdiresa= fields.Boolean('Visto Bueno DIRESA',default=False)
    observacion_ogcti=fields.Text('Observacion OGCTI', translate=True)
    user_diresa=fields.Many2many('res.users','usuarios')
    users_access_ids=fields.Many2many('res.users','rel_mision_users','requisito_id','user_id',store=True,compute='_compute_users_access_ids')   
    informediresas_ids = fields.Many2many('ir.attachment', string="Informe tecnico diresa",help="Adjuntar informe tecnico diresa")
    informedisas_ids = fields.Many2many('ir.attachment', string="Informe tecnico diresa",help="Adjuntar informe tecnico disa")
    convenios=fields.Binary('Convenios', store=True,attachment=True)
    name_filename_convenios=fields.Char('Nombre del convenio')
    resolucion_ministerial=fields.Binary('Resolucion ministerial', store=True,attachment=True)
    name_filename_resolucion_ministerial=fields.Char('Nombre de la resolucion ministerial')

    @api.depends('listaprofesionales_ids')
    def _compute_users_access_ids(self):
        for record in self:
            user_listas = [item.user_colegiado.ids for item in record.listaprofesionales_ids]
            user_ids = []
            for item in user_listas:
                user_ids.extend(item)

        if user_ids:      
            record.users_access_ids = [(6, 0, user_ids)]
      
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

    @api.depends('enviar_disa','enviar_diresa','state','vdiresa','vdisa','users_access_ids','user_diresa')
    def _compute_email(self):
        for record in self:
            depend=()
            cont=[]

            if record.state=='01' or record.state=='V':                  
                donatario=self.browse(self.id)           
                correos=donatario.create_uid.email

            else:
                if record.state=='I':  
                    group_ogcti=ref_xml_id(self,'donacion','group_donacion_requisito_ogcai')
                    depend=depend+(group_ogcti,)  
                 
                else:
                    if record.state=='R': 
                        if record.vdisa==False and record.vdiresa==False:

                            for user_coleg in record.users_access_ids:
                                user=self.env['res.users'].browse(user_coleg.id)
                                email=user.partner_id.email
                                cont.append(email)

                            for user_diresa in record.user_diresa:
                                user=self.env['res.users'].browse(user_diresa.id)
                                email=user.partner_id.email
                                cont.append(email)  
                            
                        else:
                            
                            if record.vdisa==True or record.vdiresa==True:
                                donatario=self.browse(self.id)           
                                donatariocorreo=donatario.create_uid.email
                                cont.append(donatariocorreo)
                                #depend=depend+('OGCTI',) 
                                group_ogcti=ref_xml_id(self,'donacion','group_donacion_requisito_ogcai')
                                depend=depend+(group_ogcti,)                 


                if depend:

                    for group in depend:
                        usuarios=self.env['res.groups'].browse(group.id).users
                    
                        for x in usuarios:                            
                            user=self.env['res.users'].browse(x.id)
                            email=user.partner_id.email
                            cont.append(email)
                 
                        correos=','.join(cont)
                else:
                        correos=','.join(cont)

        record.email_to = correos


    # ACCIONES DEL WORKFLOW FLUJO NORMAL
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
        self.vdisa = True         
        self.send_mail_template_m()
        return True

    @api.one
    def visto_diresa(self):
        self.vdiresa = True           
        self.send_mail_template_m()
        return True

    @api.multi
    def send_mail_template_m(self):  
        template = self.env.ref('donacion.email_template_mision')       
        return self.env['mail.template'].browse(template.id).send_mail(self.id,force_send=True)


class Listaprofesionales(models.Model):
    _name='mision.listaprofesionales'
    name = fields.Char('Nombre', required=True)
    institucion=fields.Char('Institucion') 
    pais = fields.Many2one('res.country','Pais de procedencia')    
    # especialidad=fields.Many2one('mision.categoriaprofesional','Categoria profesional')
    user_colegiado=fields.Many2one('res.users','usuario colegiado')
    pasaporte= fields.Binary('Fotocopia simple de Pasaporte',store=True,attachment=True) 
    titulo= fields.Binary('Fotocopia simple de Titulo Profesional',store=True,attachment=True) 
    licencia= fields.Binary('Fotocopia simple de licencia para ejercer su profesion en su pais',store=True,attachment=True) 
    cv= fields.Binary('Curriculum Vitae',store=True,attachment=True)
    mision_id=fields.Many2one('mision.requisito','misiones')
    #rol_id_user=fields.Char(compute='_compute_roluser')
    habilitar=fields.Boolean('Habilitar', default=False)
    documento_habilitacion= fields.Binary('Documento de habilitacion',store=True,attachment=True) 

    
class Subirarchivos(models.Model):
    _name = 'website.archive'

    def _get_csv_url(self):
        self.csv_url = "/csv/download/{}/".format(self.id)

    name=fields.Char('nombre')
    file = fields.Binary('File')
    file_name=fields.Char('Nombre del archivo')
    csv_url = fields.Char(compute=_get_csv_url)        

    @api.model
    def _csv_download(self,vals):

        return None