#/usr/bin/python
import sys, json, xmpp, os, logging, time
import googledatastore as datastore

SERVER = 'gcm.googleapis.com'
PORT = 5236 # change to 5235 for production
USERNAME = os.environ.get('PROJECT_NUM')
PASSWORD = os.environ.get('GCM_API_KEY')
datastore.set_options(dataset=os.environ.get('PROJECT_ID'))
logging.basicConfig(format='%(asctime)-15s %(levelname)s: %(message)s', level=logging.INFO)

def send(json_dict):
  template = ("<message><gcm xmlns=\"google:mobile:data\">{0}</gcm></message>")
  message = xmpp.protocol.Message(node=template.format(json.dumps(json_dict, separators=(',', ':'))))
  client.send(message)

def message_callback(session, message):
  gcm = message.getTags('gcm')

  if gcm:
    gcm_json = gcm[0].getData()
    msg = json.loads(gcm_json)
    msg_id = msg["message_id"]
    device_reg_id = msg["from"]

    if msg.has_key('message_type'):
      logging.info('Received GCM ack: ' + msg_id)
    else:
      logging.info('Received GCM message: ' + msg_id)
      # Acknowledge the incoming message immediately.
      send({"to": device_reg_id,
            "message_id": msg_id,
            "message_type": "ack"})
      logging.info('Acknowledged GCM message: ' + msg_id)
      # Handle action
      if msg.has_key('data'):
        data = msg["data"]
        if data.has_key('action'):
          logging.info('Processing action: ' + data["action"])
          uid = data["uid"]
          password = data["password"]
          try:
            if data["action"] == "upload_profile":
              add_user(uid, password, data["token"], data["emoji_1"], data["emoji_2"], data["emoji_3"],
                       data["generated_name"], data["gender"], data["location"], data["radius"])
            else:
              user = auth_user(uid, password, data["action"])
              if user == 404:
                if data["action"] == "update_profile":
                  add_user(uid, password, data["token"], data["emoji_1"], data["emoji_2"], data["emoji_3"],
                           data["generated_name"], data["gender"], data["location"], data["radius"])
              elif user != 403:
                if data["action"] == "send_message":
                  send_message(uid, data["to"], data["message"], get_timestamp())
                elif data["action"] == "lookup_nearby":
                  lookup_nearby(uid, user, data["radius"])
                elif data["action"] == "lookup_profile":
                  lookup_profile(uid, user, data["profile"])
                elif data["action"] == "update_profile":
                  data_dict = {"token": data["token"],
                               "emoji_1": data["emoji_1"], "emoji_2": data["emoji_2"], "emoji_3": data["emoji_3"],
                               "generated_name": data["generated_name"], "gender": data["gender"],
                               "location": data["location"], "radius": data["radius"]}
                  update_user(uid, user, data_dict, data["action"])
                elif data["action"] == "update_token":
                  update_user(uid, user, {"token": data["token"]}, data["action"])
                elif data["action"] == "delete_profile":
                  del_user(uid)

          except datastore.RPCError as e:
            # RPCError is raised if any error happened during a RPC.
            # It includes the `method` called and the `reason` of the
            # failure as well as the original `HTTPResponse` object.
            logging.error('Error while doing datastore operation')
            logging.error('RPCError: %(method)s %(reason)s',
                          {'method': e.method,
                           'reason': e.reason})
            logging.error('HTTPError: %(status)s %(reason)s',
                          {'status': e.response.status,
                           'reason': e.response.reason})

def add_user(uid, password, token, emoji_1, emoji_2, emoji_3, generated_name, gender, location, radius):
  req = datastore.CommitRequest()
  req.mode = datastore.CommitRequest.NON_TRANSACTIONAL

  user = req.mutation.insert.add()
  path_element = user.key.path_element.add()
  path_element.name = uid
  path_element.kind = 'User'
  current_time = long(time.time() * 1e6)

  password_property = user.property.add()
  password_property.name = 'password'
  password_property.value.string_value = password
  token_property = user.property.add()
  token_property.name = 'token'
  token_property.value.string_value = token
  emoji_1_property = user.property.add()
  emoji_1_property.name = 'emoji_1'
  emoji_1_property.value.string_value = emoji_1
  emoji_2_property = user.property.add()
  emoji_2_property.name = 'emoji_2'
  emoji_2_property.value.string_value = emoji_2
  emoji_3_property = user.property.add()
  emoji_3_property.name = 'emoji_3'
  emoji_3_property.value.string_value = emoji_3
  generated_name_property = user.property.add()
  generated_name_property.name = 'generated_name'
  generated_name_property.value.string_value = generated_name
  gender_property = user.property.add()
  gender_property.name = 'gender'
  gender_property.value.string_value = gender
  location_property = user.property.add()
  location_property.name = 'location'
  location_property.value.string_value = location
  radius_property = user.property.add()
  radius_property.name = 'radius'
  radius_property.value.string_value = radius
  date_created_property = user.property.add()
  date_created_property.name = 'date_created'
  date_created_property.value.timestamp_microseconds_value = current_time
  date_modified_property = user.property.add()
  date_modified_property.name = 'date_modified'
  date_modified_property.value.timestamp_microseconds_value = current_time

  datastore.commit(req)
  logging.info('Added user: ' + uid + ' (' + generated_name + ')')

def del_user(uid):
  user_key = datastore.Key()
  path = user_key.path_element.add()
  path.name = uid
  path.kind = 'User'

  req = datastore.CommitRequest()
  req.mode = datastore.CommitRequest.NON_TRANSACTIONAL
  req.mutation.delete.extend([user_key])
  datastore.commit(req)
  logging.info('Deleted user: ' + uid)

def auth_user(uid, password, action):
  user_key = datastore.Key()
  path = user_key.path_element.add()
  path.name = uid
  path.kind = 'User'

  req = datastore.LookupRequest()
  req.key.extend([user_key])
  resp = datastore.lookup(req)

  if len(resp.missing) is 1:
    logging.error('Entity not found for user: ' + uid + ' action: ' + action)
    return 404
  user = resp.found[0].entity

  if action != "lookup":
    for prop in user.property:
      if prop.name == 'password':
        if password != prop.value.string_value:
          logging.error('Access denied for user: ' + uid + ' action: ' + action)
          return 403
    logging.info('Authenticated user: ' + uid + ' action: ' + action)

  return user

def lookup_profile(uid, user, target_uid):
  target_user = auth_user(target_uid, "", "lookup")
  user_dict = {}

  if target_user != 404:
    data_dict = {}
    for prop in target_user.property:
      if prop.name in ['emoji_1', 'emoji_2', 'emoji_3', 'generated_name', 'gender']:
        data_dict[prop.name] = prop.value.string_value
    user_dict[target_uid] = data_dict
  else:
    user_dict[target_uid] = "404"

  token = get_token(user)
  message_id = next_message_id(token)
  send({"to": token,
        "message_id": message_id,
        "data": {
          "response_type": "lookup_profile",
          "body": user_dict,
          "timestamp": get_timestamp()
        }})

  logging.info('Profile lookup response sent to user: ' + uid + ' message_id: ' + message_id)

def lookup_nearby(uid, user, radius):
  req = datastore.RunQueryRequest()
  query = req.query
  query.kind.add().name = 'User'
  resp = datastore.run_query(req)
  user_dict = {}

  for entity_result in resp.batch.entity_result:
    found_user = entity_result.entity
    if found_user.key.path_element[0].name == uid:
      continue
    data_dict = {}
    for prop in found_user.property:
      if prop.name in ['emoji_1', 'emoji_2', 'emoji_3', 'generated_name', 'gender']:
        data_dict[prop.name] = prop.value.string_value
    user_dict[found_user.key.path_element[0].name] = data_dict

  token = get_token(user)
  message_id = next_message_id(token)
  send({"to": token,
        "message_id": message_id,
        "data": {
          "response_type": "lookup_nearby",
          "body": user_dict,
          "timestamp": get_timestamp()
        }})

  logging.info('Nearby lookup response sent to user: ' + uid + ' message_id: ' + message_id)

def update_user(uid, user, data_dict, action):
  for prop in user.property:
    if data_dict.has_key(prop.name):
      prop.value.string_value = data_dict[prop.name]
    elif prop.name == 'date_modified':
      prop.value.timestamp_microseconds_value = long(time.time() * 1e6)

  req = datastore.CommitRequest()
  req.mode = datastore.CommitRequest.NON_TRANSACTIONAL
  req.mutation.update.extend([user])
  datastore.commit(req)
  logging.info('Updated user: ' + uid + ' action: ' + action)

def send_message(from_uid, to_uid, message, timestamp):
  user = auth_user(to_uid, "", "lookup")

  if user == 404:
    logging.error('Failed to send message to user: ' + to_uid)
    return 404

  token = get_token(user)
  message_id = next_message_id(token)
  send({"to": token,
        "message_id": message_id,
        "data": {
          "from_uid": from_uid,
          "body": message,
          "timestamp": timestamp
        }})

  logging.info('Message sent to user: ' + to_uid + ' message_id: ' + message_id)

def next_message_id(token):
  return token[-4:] + str(long(time.time() * 1e4))

def get_token(user):
  for prop in user.property:
    if prop.name == 'token':
      return prop.value.string_value

def get_timestamp():
  return str(long(time.time() * 1e3))

client = xmpp.Client(SERVER, debug=['socket'])
client.connect(server=(SERVER,PORT), secure=1, use_srv=False)
auth = client.auth(USERNAME, PASSWORD)
if not auth:
  print 'Authentication failed!'
  sys.exit(1)

client.RegisterHandler('message', message_callback)

while True:
  try:
    client.Process(1)
  except Exception as e:
    print e.__doc__
    print e.message
    break