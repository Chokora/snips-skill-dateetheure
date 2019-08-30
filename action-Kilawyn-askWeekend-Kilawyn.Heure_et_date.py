#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions
from hermes_python.ontology import *
import io
import toml

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(configparser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, configparser.Error) as e:
        return dict()

def subscribe_intent_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper(hermes, intentMessage, conf)


def action_wrapper(hermes, intentMessage, conf):
    """ Write the body of the function that will be executed once the intent is recognized. 
    In your scope, you have the following objects : 
    - intentMessage : an object that represents the recognized intent
    - hermes : an object with methods to communicate with the MQTT bus following the hermes protocol. 
    - conf : a dictionary that holds the skills parameters you defined. 
      To access global parameters use conf['global']['parameterName']. For end-user parameters use conf['secret']['parameterName'] 
     
    Refer to the documentation for further details. 
    """
    import datetime
    import random

    now = datetime.date.today()
    counter = (6 - today.weekday())
    is_weekend = False
    if counter >= 5:
        is_weekend = True
    weekend_sentences = [
        "C'est parfait ! C'est le week-end.",
        "Ouf, nous sommes en week-end",
        "On dirait que tu dors, c'est le week-end",
    ]
    week_sentences = [
        "C'est dur, encore %d jours jusqu'au week-end",
        "Courage ! Plus que %d jours jusqu'au week-end",
        "Il semblerait que tu sois pressé, %d jours jusqu'au week-end",
    ]

    sentence = ""
    if is_weekend:
        sentence = random.choice(weekend_sentences)
    else:
        sentence = random.choice(week_sentences) % counter
    
    hermes.publish_end_session(intentMessage.session_id, sentence)
    


if __name__ == "__main__":
    f = open("/etc/snips.toml", "rt")
    config = toml.load(f)
    mqtt_opts = MqttOptions(username=config["snips-common"]["mqtt_username"], password=config["snips-common"]["mqtt_password"], broker_address=config["snips-common"]["mqtt"])
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intent("Kilawyn:askWeek", subscribe_intent_callback) \
         .start()
