from NodePath import NodePath


class Session:
    def start(self):
        pass

    def finish(self):
        pass

    def execute(self, target: NodePath, action, *arguments):
        raise NotImplementedError("TreeView.execute method was not overridden")

    def get(self, target):
        target = NodePath.cast(target)
        return self.execute(target, 'get')

    def set(self, target, new_value):
        target = NodePath.cast(target)
        return self.execute(target, 'set', new_value)

    def list(self, target):
        target = NodePath.cast(target)
        return self.execute(target, 'list')

    def exists(self, target):
        target = NodePath.cast(target)
        return self.execute(target.base_path, 'exists', target.base_name)

    def create(self, target, value=None):
        target = NodePath.cast(target)
        return self.execute(target.base_path, 'create', target.base_name, value)

    def remove(self, target):
        target = NodePath.cast(target)
        return self.execute(target.base_path, 'remove', target.base_name)