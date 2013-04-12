A collection of various small Django utilities. Some examples:

* modelhelpers.SubclassModelMixin makes it easy to cast an instance of a base class to a subclass (if the database content actually is the subclass), making querying of entier class hierarchies easier.
* signalautoconnectmodel.SignalAutoConnectModel add signal handlers as methods with special names directly on the object
* jsonview.json_view decorator for views that return data that is converted to JSON before it is sent to the client
* jsonview.JsonEncodeRegistry / jsonview.JsonDecodeRegistry global registry of object type converters, allowing any object to be serialized/deserialized to/from json by the module
* fields.ModelLinkWidget Display a foreign key as a link to the other model in django admin
* fields.JsonField store arbitrary data in a model field, serialized as json and backed by a text database field.
* field.Base64Field store arbitrary binary data in a model field, serialized as base64 backed by a text database field.

