import os
import json

ENV = {

}

ENV_VAR_DEFINITIONS = {
	'root' : ('The root directory for storing Dyson Sphere Program',
		os.path.join(os.path.expanduser('~/Documents/Dyson Sphere Program/Blueprint')))
}

ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))

def load_env(path=ENV_PATH):
	if os.path.isfile(path):
		env = json.load(open(path))
		ENV.update(env)
	for key, (_, default) in ENV_VAR_DEFINITIONS.items():
		if key not in ENV:
			ENV[key] = default
