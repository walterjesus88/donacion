# -*- coding: utf-8 -*-

from openerp import models, fields, api
from odoo.addons.base.res import res_users

import psycopg2
import ConfigParser
import os
import pdb


class Wizard(models.TransientModel):
    _name = 'donacion.wizard'
    texto = fields.Char('Texto a buscar')
    elemento = fields.Many2one('linea',domain="[('id','in',lista_ids)]")
    lista_ids= fields.Many2many('linea',string="Buscar por DCI o nombre generico")
    donacion_id=fields.Many2one('donacion.requisito')
    
    @api.multi
    def buscar(self):
        # conectas al postgresql server
        config = ConfigParser.ConfigParser()
        current_path = os.path.split(os.path.dirname(os.path.realpath(__file__)))

        config.read(current_path[0] + '/config.ini')

        if len(config.sections()) > 0: 

            bddigemid = dict( 

                host = config.get('API', 'host'),
                password = config.get('API', 'password'),
                user = config.get('API', 'user'),
                database = config.get('API', 'database'),
                port = config.get('API', 'port'),
            )


        #src_db = psycopg2.connect(host="127.0.0.1", port="5432",database="BDDigemid", user="postgres", password="123456")     
        src_db = psycopg2.connect(**bddigemid)
        self.env['linea'].search([]).unlink()

        src_cr = src_db.cursor()        
        #if not consulta:
        # select product_template.name,product_tmpl_id,concentracion,catalogo_codigo,presentacion,denominacion_comun,fabricante_abreviado,tipo_producto from product_product 
        # inner join product_template on product_template.id=product_product.product_tmpl_id
        # WHERE tipo_producto='producto' and denominacion_comun='PARACETAMOL'

        #SELECT catalogo_codigo, denominacion_comun, concentracion, forma_farmaceutica_simpl, presentacion FROM
        #product_product WHERE tipo_producto='producto' and denominacion_comun like '%%%s%%'

        try:
            src_cr.execute("""
                SELECT catalogo_codigo,denominacion_comun,concentracion,forma_farmaceutica_simpl,product_template.name AS marca,presentacion,fabricante_abreviado
                from product_product 
                inner join product_template on product_template.id=product_product.product_tmpl_id
                WHERE tipo_producto='producto' --and denominacion_comun like '%%%s%%'  """ 
                % self.texto)

            r = src_cr.fetchall()
            for registro in r:
                consulta=self.env['linea'].search([('codigo','=',registro[0])])

                if not consulta:                            
                    values = dict(codigo=registro[0], descripcion=registro[1],concentracion=registro[2],forma_simple=registro[3],marca=registro[4])            
                    self.env['linea'].create(values)


        except psycopg2.Error as e:
            print e.pgerror


        return {
            'res_model': 'linea',
            'type':'ir.ui.view',
            'view_type': 'form',
            'view_mode': 'form',    
            'target': 'new',
            'res_id': self.id,
            'context': {}, 
        }  


    @api.model
    def create(self,vals):

        if vals['lista_ids']!=[]:

            linea_productos=vals['lista_ids'][0][2]     
                
            for registro in linea_productos: 
                buscar_registro = self.env['linea'].search([('id','=',registro)])       

                nueva_lista = dict(name=buscar_registro.marca,name_generico=buscar_registro.descripcion,concentracion=buscar_registro.concentracion,forma=buscar_registro.forma_simple,donacion_id=vals['donacion_id'])

                self.env['donacion.lista'].create(nueva_lista)

        return super(Wizard, self).create(vals)

class Wizard_Linea(models.Model):
    _name = 'linea'
    _rec_name = 'descripcion'
    codigo = fields.Char('Catalogo codigo')
    marca=fields.Char('Marca')
    descripcion = fields.Char('Nombre de concentracion')
    concentracion=fields.Char('Concentracion')
    forma_simple=fields.Char('Forma simple descripcion')




