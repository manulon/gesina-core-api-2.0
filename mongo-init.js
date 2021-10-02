db.createUser({
  user: 'app',
  pwd: 'password',
  roles: [
    {
      role: 'dbOwner',
      db: 'gesina',
    },
    {
      role: 'dbOwner',
      db: 'gesina_test',
    },
  ],
});

