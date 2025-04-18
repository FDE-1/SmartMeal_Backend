from flask import request, jsonify, current_app
from flask_restx import Namespace, Resource, fields
from ..connection.loader import db
from ..models.preferences import Preferences
from ..models.user import User
from psycopg2 import IntegrityError
import time

api = Namespace('preferences', description='User preferences operations')

preference_model = api.model('Preference', {
    'user_id': fields.Integer(required=True, description="ID of the user"),
    'allergy': fields.Raw(required=True, description="ID of the user"),
    'diet': fields.String(required=True, description="ID of the user"),
    'goal': fields.String(required=True, description="ID of the user"),
    'new': fields.Integer(required=True, description="ID of the user"),
    'number_of_meals': fields.Integer(required=True, description="ID of the user"),
    'grocery_day': fields.String(required=True, description="ID of the user"),
    'language': fields.String(required=True, description="ID of the user"),
})

preference_id_model=api.model('user_id',{
    'user_id': fields.Integer()
})

update_model = api.model('update', {
    "preference_id": fields.Integer(),
    "allergy": fields.Raw(required=True, description="ID of the user"),
    "goal": fields.String(required=True, description="ID of the user"),
    "number_of_meals": fields.Integer(required=True, description="ID of the user"),
})

@api.route('/')
class PreferenceList(Resource):
    @api.expect(preference_model)
    def post(self):
        """Create a new preference"""
        try:
            data = api.payload
            
            if not data:
                return {'error': 'Pas de donnée reçu'}, 400
            if 'user_id' not in data:
                return {'error': 'user_id non reçu'}, 400
           
            new_preference = Preferences(
                user_id=data['user_id'],
                allergy=data.get('allergy', []),  
                diet=data.get('diet', ''),
                goal=data.get('goal', ''),
                new=data.get('new', 1),
                number_of_meals=data.get('number_of_meals', 3),
                grocery_day=data.get('grocery_day', 'Monday'),
                language=data.get('language', 'fr')
            )
            
            db.session.add(new_preference)
            db.session.flush()
            db.session.commit()  
            
            return {
                'message': 'Préférence créée',
                'preference_id': new_preference.preference_id
            }, 201

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur création préférence: {str(e)}")
            return {'error': f"Erreur serveur: {str(e)}"}, 500
    
@api.route('/id')
class PreferenceById(Resource):
    @api.expect(preference_id_model)
    def get(self):
        """Recupere la preference selon user_id"""
        try:
            data = api.payload
            preference = Preferences.query.filter_by(user_id=data['user_id']).first()       
            if not preference:
                return {'message': 'Preference pas trouvé'}, 404
            return {
                'preference_id': preference.preference_id,
                'user_id': preference.user_id,
                'allergy': preference.allergy,
                'diet': preference.diet,
                'goal': preference.goal,
                'new': preference.new,
                'number_of_meals': preference.number_of_meals,
                'grocery_day': preference.grocery_day,
                'language': preference.language
            },200
        except Exception as e:
            db.session.rollback()
            api.abort(500, "Erreur lors de la supprésion", error=str(e))

    @api.expect(update_model)
    def put(self):
        """Met à jour la préférence selon l'utilisateur id, et ajoute les nouvelles allergies sans dupliquer"""
        try:
            data = api.payload
            
            if not data:
                return {'message': 'Aucune donnée reçue'}, 400
            if 'preference_id' not in data:
                return {'message': 'preference_id est requis'}, 400

            preference = Preferences.query.filter_by(preference_id=data['preference_id']).first()
            if not preference:
                return {'message': 'Préférence pas trouvée'}, 404
            # print("before" + str(preference.allergy))
            current_app.logger.debug(f"Before update - Allergy: {preference.allergy} | Diet: {preference.diet}")

            for key, value in data.items():
                if key == 'preference_id':
                    continue  
                    
                if key == 'allergy':
                    if not isinstance(value, list):
                        return {'message': 'Le champ allergy doit être une liste de chaînes'}, 400
                    
                    existing_allergies = preference.allergy or []
                    new_allergies = [a for a in value if a not in existing_allergies]
                    preference.allergy = existing_allergies + new_allergies
                else:
                    setattr(preference, key, value)

            # print("after" + str(preference.allergy))

            db.session.flush()  
            db.session.commit()
            # updated_pref = db.session.query(Preferences).filter_by(
            #                 preference_id=data['preference_id']
            #             ).first()
                        
            # if updated_pref.allergy != preference.allergy:
            #     raise RuntimeError("La mise à jour n'a pas persisté en base de données")

            return {
                'message': 'Préférence mise à jour',
                'preference_id': preference.preference_id,
                'user_id': preference.user_id,
                'allergy': preference.allergy,
                'updated_fields': list(data.keys())
            }, 200

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur mise à jour préférence: {str(e)}\n{traceback.format_exc()}")
            return {'message': 'Erreur lors de la mise à jour', 'error': str(e)}, 500
    
    @api.expect(preference_id_model)
    def delete(self):
        """Supprime la preference"""
        try:
            data = api.payload
            preference = Preferences.query.filter_by(user_id=data['user_id']).first()          
            db.session.delete(preference)
            db.session.commit()
            return {'message': 'Preference deleted'}
        except Exception as e:
            db.session.rollback()
            api.abort(500, "Erreur lors de la mise à jour", error=str(e))

@api.route('/testsuite')
class PreferenceTestSuite(Resource):
    @api.doc('run_preference_test_suite')
    @api.response(200, 'Succès')
    @api.response(500, 'Erreur du serveur')
    def post(self):
        """Exécute une suite de tests complète pour les préférences"""
        résultats = []
        preference_id = None
        test_user_id = 5  # ID spécial pour les tests

        def unpack_response(resp):
            """Gère les tuples de Flask RESTx"""
            if isinstance(resp, tuple):
                time.sleep(0.2)
                return resp[0], resp[1]
            return resp, 200

        try:
            # === Test 1: Création des préférences ===
            create_payload = {
                "user_id": test_user_id,
                "allergy": ["gluten", "lactose"],
                "diet": "vegetarian",
                "goal": "weight_loss",
                "new": 1,
                "number_of_meals": 3,
                "grocery_day": "Monday",
                "language": "fr"
            }

            with current_app.test_request_context(json=create_payload):
                response = PreferenceList().post()
                pref_obj, status_code = unpack_response(response)
                preference_id = pref_obj['preference_id']
                résultats.append(f"✅ Préférences créées avec ID : {preference_id}")

            # === Test 2: Récupération par user_id ===
            with current_app.test_request_context(json={"user_id": test_user_id}):
                response = PreferenceById().get()
                data, status_code = unpack_response(response)
                if status_code != 200:
                    raise Exception("Échec de récupération par user_id")
                if data['diet'] != "vegetarian":
                    raise Exception("Données incorrectes récupérées")
                résultats.append(f"✅ Préférences récupérées : {data}")

            # === Test 3: Mise à jour partielle ===
            update_payload = {
                "preference_id": preference_id,
                "allergy": ["fruits de mer"],
                "goal": "muscle_gain",
                "number_of_meals": 4
            }

            with current_app.test_request_context(json=update_payload):
                response = PreferenceById().put()
                _, status_code = unpack_response(response)
                if status_code != 200:
                    raise Exception("Échec de la mise à jour")
                résultats.append("✅ Mise à jour partielle effectuée")

            # === Test 4: Vérification fusion allergies ===
            with current_app.test_request_context(json={"user_id": test_user_id}):
                response = PreferenceById().get()
                updated, _ = unpack_response(response)
                allergies = updated['allergy']
                print(allergies)
                if not (set(allergies) == {"gluten", "lactose", "fruits de mer"}):
                    raise Exception("Échec de la fusion des allergies")
                if updated['number_of_meals'] != 4:
                    raise Exception("Échec de mise à jour des repas")
                résultats.append("✅ Fusion des allergies et mise à jour vérifiée")

            # === Test 5: Suppression ===
            with current_app.test_request_context(json={"user_id": test_user_id}):
                response = PreferenceById().delete()
                _, status_code = unpack_response(response)
                if status_code != 200:
                    raise Exception("Échec de suppression")
                résultats.append("✅ Préférences supprimées avec succès")

            # Vérification finale
            deleted_pref = Preferences.query.filter_by(user_id=test_user_id).first()
            if deleted_pref:
                raise Exception("La suppression n'a pas fonctionné")

            résultats.append("\n🏁 Tous les tests des préférences sont passés avec succès !")
            return {'résultats': résultats}, 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            db.session.rollback()
            
            # Nettoyage si échec
            if preference_id:
                pref = Preferences.query.get(preference_id)
                if pref:
                    db.session.delete(pref)
                    db.session.commit()
            
            résultats.append(f"\n❌ Erreur pendant les tests : {str(e)}")
            return {'résultats': résultats}, 500