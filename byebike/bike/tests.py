from django.test import TestCase
from django.contrib.auth.models import User

# Create your tests here.
from .models import Item, ShippingAddress


class BikeCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='ecommerce', email='test@test.com')
        self.credential = {'username': 'test', 'password': 'ecommerce'}
        self.item = Item.objects.create(titolo="Bicicletta",
                                        descrizione="Bicicletta",
                                        tipologia="B",
                                        immagine="n",
                                        categoria="C",
                                        condizione='N',
                                        genere="U",
                                        prezzo="300",
                                        venditore=self.user)

        self.address = ShippingAddress.objects.create(user=self.user,
                                                      città="Modena",
                                                      stato="O",
                                                      cap="48521",
                                                      via="n",
                                                      interno="3",
                                                      note="ciao")
        self.user2 = User.objects.create_user(username='test2', email='test2@test.com', password='ecommerce')
        self.credential2 = {'username': 'test2', 'password': 'ecommerce'}


    def test_item_create(self):
        '''
        Verifico che nell' inserimento di un articolo i campi obbligatori siano rispettati
        '''
        self.client.login(**self.credential)
        response = self.client.post('/createitem/', {})
        self.assertFormError(response, 'form', 'titolo', 'Questo campo è obbligatorio.')
        self.assertFormError(response, 'form', 'descrizione', 'Questo campo è obbligatorio.')
        self.assertFormError(response, 'form', 'tipologia', 'Questo campo è obbligatorio.')
        self.assertFormError(response, 'form', 'immagine', 'Questo campo è obbligatorio.')
        self.assertFormError(response, 'form', 'categoria', 'Questo campo è obbligatorio.')
        self.assertFormError(response, 'form', 'condizione', 'Questo campo è obbligatorio.')
        self.assertFormError(response, 'form', 'genere', 'Questo campo è obbligatorio.')
        self.assertFormError(response, 'form', 'prezzo', 'Questo campo è obbligatorio.')

        self.assertTemplateUsed(response, 'bike/item_create.html')
        self.assertEqual(response.status_code, 200)  # verifica per capire se il template utilizzato è quello corretto

        response = self.client.post('/createitem/',
                                    {'titolo': 'Bicicletta Rosa', 'descrizione': 'rosa', 'tipologia': 'U', 'immagine': 's', 'categoria': 'C', 'condizione': 'U', 'genere': 'U', 'prezzo': '1250'})
        self.assertTemplateUsed(response, 'bike/item_create.html')
        self.assertEqual(response.status_code, 200)


    '''
    Test per verificare se all' inserimento di un articolo, un utente non loggato
    viene reindirizzato prima nella schermata di login.
    '''
    def test_login_required(self):
        response = self.client.get('/createitem/')
        self.assertRedirects(response, '/accounts/login/?next=/createitem/')
        # 302 --> FOUND: pagina esiste ma non puoi entrarci
        self.assertEqual(response.status_code, 302)


    '''
    Test per il cambio dell' indirizzo di un utente 
    '''
    def test_address_change(self):
        # con utente autenticato
        self.client.login(**self.credential)
        response = self.client.get('/user/address/' + str(self.address.id) + '/modify/')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/user/address/' + str(self.address.id) + '/modify/', {})
        self.assertFormError(response, 'form', 'città', 'Questo campo è obbligatorio.')
        self.assertFormError(response, 'form', 'via', 'Questo campo è obbligatorio.')
        self.assertFormError(response, 'form', 'stato', 'Questo campo è obbligatorio.')
        self.assertFormError(response, 'form', 'cap', 'Questo campo è obbligatorio.')
        response = self.client.post('/user/address/' + str(self.address.id) + '/modify/',
                                    {'città': 'chieti', 'via': 'strada', 'stato': 'it', 'cap': '85710'})
        self.assertRedirects(response, '/user/' + self.user.username + '/address_page/')
        self.client.logout()

        # con utente  autenticato ma non creatore
        self.client.login(**self.credential2)
        response = self.client.get('/user/address/' + str(self.address.id) + '/modify/')
        self.assertTemplateUsed(response, 'bike/homepage.html')
        self.assertTemplateNotUsed(response, 'accounts/address_change.html')


    ''' 
    Test per l' eliminazione di un indirizzo dell' utente
    '''
    def test_address_delete(self):
        # con utente autenticato
        self.client.login(**self.credential)
        response = self.client.get('/user/address/' + str(self.address.id) + '/delete/')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/user/address/' + str(self.address.id) + '/delete/', {})
        self.assertRedirects(response, '/user/' + self.user.username + '/address_page/')
        self.client.logout()

        # con utente autenticato ma non creatore
        self.client.login(**self.credential2)
        response = self.client.get('/user/address/' + str(self.address.id) + '/delete/')
        self.assertTemplateNotUsed(response, 'accounts/address_delete.html')
