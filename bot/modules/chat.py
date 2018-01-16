import json
import requests

from bot import app
from bot import manager

from flask import request

from bot.modules.tables import User
from bot.modules.dialogs import Dialog
from bot.modules.toolbox import ToolBox

from bot.modules.components import Button

FB_SITE_TOKEN, FB_VERIFY_TOKEN = ToolBox.load_config()


buttons = [
        Button('postback', 'Ver cabelos', 'Cabelos'),
        Button('postback', 'Dúvidas frequentes', 'Dúvidas'),
        Button('postback', 'Fale conosco', 'Fale conosco')
    ]

class Bot():
    '''
        Classe do bot
    '''


    @app.route('/', methods = [ 'GET' , 'POST' ])
    def hook():
        '''
            Método que faz o tratamento das requisições/envios
        '''

        if request.method == 'POST':
            '''
                Adicione os tratamentos das mensagens enviadas de seu bot aqui
            '''

            user = None
            data = json.loads(request.data.decode())
            user_sender_id = data['entry'][0]['messaging'][0]['sender']['id']

            # Buscando o cadastro do usuário no banco de dados
            user = User.query.filter_by(_id = user_sender_id).first()

            # Caso o usuário não seja encontrado, ele será registrado
            if user == None:
                _infos = Dialog.get_fb_date(user_sender_id)
                ToolBox.register_user(
                        User(
                            user_sender_id,
                            _infos[0],
                            _infos[1],
                            _infos[2])
                        )

                Dialog.send_message('Seja bem-vindo {{user_first_name}}, vou ser seu assistente =D',
                                     user_sender_id)
                Dialog.send_message('Para interagir comigo, basta ir clicando nos botões que eu envio',
                                    user_sender_id)

                Dialog.send_buttons(buttons, 'Selecione uma opção', user_sender_id)

            if 'message' in data['entry'][0]['messaging'][0]:

                Dialog.send_message('Opa %s ! Acho que eu não estou entendendo o que você está falando.\
                                    Para eu poder te ajudar, utilize os botões' % user.first_name,
                                    user_sender_id)
                Dialog.send_buttons(buttons, 'Selecione uma opção', user_sender_id)

            if 'postback' in data['entry'][0]['messaging'][0]:

                text = data['entry'][0]['messaging'][0]['postback']['payload']

                if text == 'Cabelos':
                    Dialog.send_message('Vou mandar as fotos =D',
                    user_sender_id)

                    Dialog.send_media_attached('image',
                                               user_sender_id,
                                               ToolBox.load_attachs())
                    Dialog.send_message('E ai o que achou ? Bacana né ?',
                                        user_sender_id)

                    Dialog.send_message('Entre em contato conosco para saber mais',
                                        user_sender_id)

                    Dialog.send_message('Whatsapp: 1234-56789',
                                        user_sender_id)

                    Dialog.send_buttons(buttons,
                                        'Se quiser ver outras coisas, aqui vai as opções',
                                        user_sender_id)

                elif text == 'Fale conosco':
                    Dialog.send_message('Fale conosco pelo Whatsapp: 12-9876543210, ou ',
                                        user_sender_id)
                    Dialog.send_buttons([Button('phone_number',
                                                'Ligue agora !',
                                                '+5512996452450')],
                                        'fale com nossos profissionais',
                                        user_sender_id)


                elif text == 'Dúvidas':
                    # ToDo - Mandar um FAQ
                    Dialog.send_message('Estou gerando um FAQ (Perguntas frequentes)',
                                        user_sender_id)
                    Dialog.send_message('Perguntas\n 1° - Existe a possíbilidade de retoque, caso necessário ?\n\t - Sim, fazemos o retoque se necessário\n2° - Quais as formas de pagamento ?\n\t - Cartão de crédio/débito, dinheiro',
                                        user_sender_id)

                    Dialog.send_buttons(buttons, 'Caso queira ver outra opção',
                                        user_sender_id)

                elif text == 'Começar':

                    Dialog.send_message('Seja bem-vindo %s, eu sou seu assistente pessoal \n \
                                        Para que eu possa te ajudar escolha um dos botões' %
                                        user.first_name,
                                        user_sender_id)
                    Dialog.send_buttons(buttons)


        elif request.method == 'GET':
            '''
                Adicione os tratamento das mensagens recebidas de seu bot aqui
            '''

            if request.args.get('hub.verify_token') == FB_VERIFY_TOKEN:

                # Configurando o greeting e get_started
                Dialog.send_greeting(
                        'Hello {{user_first_name}} !',
                        'pt_BR', '{{user_first_name}} , este é o assistente que você precisa !'
                    )

                Dialog.send_get_started('Iniciar')

                return request.args.get('hub.challenge')
            return 'Failed to verify token'

        return 'No reply'

bot = Bot()
