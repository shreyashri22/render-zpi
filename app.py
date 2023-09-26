from flask import Flask, jsonify,request
# from flask_restful import Resource,Api
from maincode import Ask_bot

# load_dotenv()
app=Flask(__name__)
# api=Api(app)

@app.route('/',methods=['GET','POST'])
def Hi():
    if (request.method=='GET'):
        data='hello'
        return jsonify({'data':data})

@app.route('/ask/<string:session_id>/<string:query>',methods = ['GET'])
def Ask(session_id,query):
    res= Ask_bot(query,session_id)
    return jsonify({'response':res})
  

if __name__ == '__main__':
  
    app.run(debug = True,host="0.0.0.0")
