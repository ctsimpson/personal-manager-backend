// MongoDB initialization script for production deployment

// Create application user and database
// Connect to admin database
db = db.getSiblingDB('admin');

// Create application user if not exists
try {
    const existingUser = db.getUser("appuser");
    print("Application user already exists");
} catch (error) {
    // User doesn't exist, create it
    db.createUser({
        user: "appuser",
        pwd: process.env.MONGODB_APP_PASSWORD || "changeme",
        roles: [
            {
                role: "readWrite",
                db: process.env.MONGO_INITDB_DATABASE || "personal_manager"
            }
        ]
    });
    print("Application user created successfully");
}

// Switch to application database
db = db.getSiblingDB('personal_manager');

// Create collections with indexes
db.createCollection("users");
db.createCollection("tasks");
db.createCollection("projects");
db.createCollection("sessions");

// Create indexes for better performance
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "created_at": 1 });

db.tasks.createIndex({ "user_id": 1 });
db.tasks.createIndex({ "created_at": 1 });
db.tasks.createIndex({ "due_date": 1 });
db.tasks.createIndex({ "status": 1 });

db.projects.createIndex({ "user_id": 1 });
db.projects.createIndex({ "created_at": 1 });

db.sessions.createIndex({ "expires_at": 1 }, { expireAfterSeconds: 0 });
db.sessions.createIndex({ "user_id": 1 });

print("Database initialization completed successfully");
print("Collections created: " + db.getCollectionNames().join(", "));
print("Ready for Personal Manager Backend application");