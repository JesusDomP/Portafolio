class ReadOnlyRouter:
    def db_for_write(self, model, **hints):
        return None  # bloquea escrituras

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return False