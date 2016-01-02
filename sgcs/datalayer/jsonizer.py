import copy

import collections


class SimpleJsonNode(object):
    def to_json(self, jsonizer):
        name = type(self).__name__
        node_dict = copy.copy(self.__dict__)
        for field, value in self.__dict__.items():
            if isinstance(value, SimpleJsonNode):
                node_dict[field] = jsonizer.to_json(value)
            elif isinstance(value, collections.Iterable):
                node_dict[field] = list(
                    jsonizer.to_json(x) if isinstance(x, SimpleJsonNode) else x for x in value)

        node_dict[jsonizer.node_id] = name
        return node_dict

    @staticmethod
    def is_complex_json(jsonizer, value):
        return isinstance(value, dict) and jsonizer.node_id in value

    def from_json(self, state, jsonizer):
        for field, value in state.items():
            if self.is_complex_json(jsonizer, value):
                state[field] = jsonizer.from_json(value)
            elif isinstance(value, collections.Iterable):
                # noinspection PyTypeChecker
                state[field] = list(jsonizer.from_json(x) if self.is_complex_json(jsonizer, value)
                                    else x for x in value)

        self.__dict__ = state
        return self


class ConfigurationJsonizer(object):
    node_id = '_node_id'

    def __init__(self, expected_classes):
        self._expected_classes = dict()
        for cls in expected_classes:
            self._expected_classes[cls.__name__] = cls

    def to_json(self, configuration_object):
        return configuration_object.to_json(self)

    def from_json(self, json):
        class_name = json[self.node_id]
        class_object = self._expected_classes.get(class_name)
        if class_object is None:
            raise UnexpectedSimpleNodeClassError(class_name)
        instance = class_object()
        state = copy.copy(json)
        del state[self.node_id]
        instance.from_json(state, self)
        return instance


class UnexpectedSimpleNodeClassError(Exception):
    def __init__(self, class_name):
        super().__init__(class_name)
        self.class_name = class_name