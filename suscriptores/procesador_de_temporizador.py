#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------
# Archivo: procesador_de_temporizador.py
# Capitulo: 3 Estilo Publica-Subscribe
# Autor(es): Luis Fernando Bollain Goytia Hernandez
#            Luis Alberto Garcia Torres
#            Carlos Alberto Aguado Chaires
# Version: 1.0 octubre 2017
# Descripción:
#
#   Esta clase define el rol de un suscriptor, es decir, es un componente que recibe mensajes.
#
#   Las características de ésta clase son las siguientes:
#
#                                   procesador_de_posicion.py
#           +-----------------------+-------------------------+------------------------+
#           |  Nombre del elemento  |     Responsabilidad     |      Propiedades       |
#           +-----------------------+-------------------------+------------------------+
#           |                       |                         |  - Se suscribe a los   |
#           |                       |                         |    eventos generados   |
#           |                       |  - Procesar valores     |    por el wearable     |
#           |     Procesador de     |    de hora y medicina   |    Xiaomi My Band.     |
#           |     posicion          |                         |  - Define la hora que  |
#           |                       |                         |    se debe tomar la    |
#           |                       |                         |    medicina            |
#           |                       |                         |  - Notifica al monitor |
#           |                       |                         |    cuando es hora de   |
#           |                       |                         |    algun medicamento.  |
#           +-----------------------+-------------------------+------------------------+
#
#   A continuación se describen los métodos que se implementaron en ésta clase:
#
#                                               Métodos:
#           +------------------------+--------------------------+-----------------------+
#           |         Nombre         |        Parámetros        |        Función        |
#           +------------------------+--------------------------+-----------------------+
#           |                        |                          |  - Recibe los signos  |
#           |       consume()        |          Ninguno         |    vitales vitales    |
#           |                        |                          |    desde el distribui-|
#           |                        |                          |    dor de mensajes.   |
#           +------------------------+--------------------------+-----------------------+
#           |                        |  - ch: propio de Rabbit. |  - Procesa y detecta  |
#           |                        |  - method: propio de     |    valores extremos   |
#           |                        |     Rabbit.              |    de la posicion.    |
#           |       callback()       |  - properties: propio de |                       |
#           |                        |     Rabbit.              |                       |
#           |                        |  - body: mensaje recibi- |                       |
#           |                        |     do.                  |                       |
#           +------------------------+--------------------------+-----------------------+
#           |    string_to_json()    |  - string: texto a con-  |  - Convierte un string|
#           |                        |     vertir en JSON.      |    en un objeto JSON. |
#           +------------------------+--------------------------+-----------------------+
#
#
#           Nota: "propio de Rabbit" implica que se utilizan de manera interna para realizar
#            de manera correcta la recepcion de datos, para éste ejemplo no hubo necesidad
#            de utilizarlos y para evitar la sobrecarga de información se han omitido sus
#            detalles. Para más información acerca del funcionamiento interno de RabbitMQ
#            puedes visitar: https://www.rabbitmq.com/
#
#-------------------------------------------------------------------------
import pika
import sys
sys.path.append('../')
from monitor import Monitor
import time


class ProcesadorPosicion:

    def consume(self):
        try:
            # Se establece la conexión con el Distribuidor de Mensajes
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
            # Se solicita un canal por el cuál se enviarán los signos vitales
            channel = connection.channel()            
            # Se declara una cola para leer los mensajes enviados por el
            # Publicador
            channel.queue_declare(queue='medicine_timer', durable=True)
            channel.basic_qos(prefetch_count=1)            
            channel.basic_consume(self.callback, queue='medicine_timer')
            channel.start_consuming()  # Se realiza la suscripción en el Distribuidor de Mensajes            
        except (KeyboardInterrupt, SystemExit):
            channel.close()  # Se cierra la conexión
            sys.exit("Conexión finalizada...")
            time.sleep(1)
            sys.exit("Programa terminado...")

    def callback(self, ch, method, properties, body):        
        hora = time.strftime("%H:%M")        
        json_message = self.string_to_json(body)        
        if json_message['medicine'] == 'paracetamol' and (hora == '00:00' or hora == '08:00' or hora == '16:=='):                        
            monitor = Monitor()
            monitor.print_notification('El paciente debe tomar paracetamol',json_message['datetime'], json_message['id'])
        
        elif json_message['medicine'] == 'ibuprofeno' and (hora == '06:00' or hora == '12:00' or hora == '18:00' or hora == '00:00'):                                
            monitor = Monitor()
            monitor.print_notification('El paciente debe tomar ibuprofeno',json_message['datetime'], json_message['id'])
        
        elif json_message['medicine'] == 'ínsulina' and (hora == '08:00' or hora == '20:00'):                                    
            monitor = Monitor()
            monitor.print_notification('El paciente debe tomar insulina',json_message['datetime'], json_message['id'])

        elif json_message['medicine'] == 'tolbutamina' and (hora == '18:00'):                        
            monitor = Monitor()
            monitor.print_notification('El paciente debe tomar ibuprofeno',json_message['datetime'], json_message['id'])

        time.sleep(1)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def string_to_json(self, string):
        message = {}
        string = string.replace('{', '')
        string = string.replace('}', '')
        values = string.split(', ')
        for x in values:
            v = x.split(': ')
            message[v[0].replace('\'', '')] = v[1].replace('\'', '')
        return message

if __name__ == '__main__':
    p_posicion = ProcesadorPosicion()
    p_posicion.consume()
