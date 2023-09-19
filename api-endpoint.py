from maincode import Ask_bot
from flask import Flask, jsonify
from flask_restful import Resource,Api

# load_dotenv()
app=Flask("askbot")
api=Api(app)

class Hi(Resource):
    def get(self):
        return("Hello")

class Ask(Resource):
    def get(self, query,session_id):
  
        return jsonify({"Response":Ask_bot(query,session_id)})
  
  
# adding the defined resources along with their corresponding urls
api.add_resource(Ask, '/ask/<session_id>/<query>')
api.add_resource(Hi,"/")

if __name__ == '__main__':
  
    app.run(debug = True)