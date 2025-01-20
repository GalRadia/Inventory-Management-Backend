from models.audit import Audit


class AuditDAO:
    def __init__(self, db):
        self.db = db
        self.collection = self.db['Audits']

    def create(self, audit: Audit):
        # Convert the Audit object to a dictionary
        audit_dict = audit.to_dict()
        # Insert the audit document into the collection
        result = self.collection.insert_one(audit_dict)
        return result.inserted_id

    def get_by_id(self, audit_id: str):
        # Find an audit log by its _id
        audit_log = self.collection.find_one({"_id": audit_id})
        return Audit.from_dict(audit_log)

    def get_all(self):
        # Get all audit logs
        audit_logs = self.collection.find()
        return [Audit.from_dict(audit) for audit in audit_logs]

    def delete(self, audit_id: str):
        # Delete an audit log by its _id
        self.collection.delete_one({"_id": audit_id})

    def update(self, audit_id: str, updated_audit: Audit):
        # Update an audit log by its _id
        self.collection.update_one(
            {"_id": audit_id},
            {"$set": updated_audit.to_dict()}
        )

    def get_by_username(self, username):
        # Find an audit log by username
        audit_log = self.collection.find_one({"username": username})
        return Audit.from_dict(audit_log) if audit_log else None
