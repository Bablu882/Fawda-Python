module.exports = {
  apps: [
    {
      name: "Fawda-app",
      script: "manage.py",
      interpreter: "python3",
      args: "runserver 0.0.0.0:4001",
      watch: true,
    }
  ]
};
