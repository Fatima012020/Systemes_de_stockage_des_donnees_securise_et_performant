// Utilise les variables d'environnement si présentes, sinon fallback
const dbName     = process.env.MONGO_APP_DB        || "donnees_medicales";
const appUser    = process.env.MONGO_APPUSER       || "appuser";
const appPwd     = process.env.MONGO_APPUSER_PWD   || "change-me-app!";
const readUser   = process.env.MONGO_READUSER      || "readonly";
const readPwd    = process.env.MONGO_READUSER_PWD  || "change-me-read!";
const backupUser = process.env.MONGO_BACKUPUSER    || "backup";
const backupPwd  = process.env.MONGO_BACKUPUSER_PWD|| "change-me-backup!";

// 1) Users applicatifs (sur la base métier)
db = db.getSiblingDB(dbName);
db.createUser({ user: appUser, pwd: appPwd, roles: [{ role: "readWrite", db: dbName }] });
db.createUser({ user: readUser, pwd: readPwd, roles: [{ role: "read", db: dbName }] });

// 2) User backup (sur admin)
db = db.getSiblingDB("admin");
db.createUser({
  user: backupUser,
  pwd: backupPwd,
  roles: [{ role: "backup", db: "admin" }, { role: "restore", db: "admin" }]
});
