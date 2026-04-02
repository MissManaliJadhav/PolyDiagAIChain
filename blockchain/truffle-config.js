module.exports = {

  networks: {
    development: {
      host: "127.0.0.1",   // Localhost
      port: 8545,          // Ganache CLI port
      network_id: "*",     // Any network
    },
  },

  mocha: {},

  compilers: {
    solc: {
      version: "0.8.21",
    }
  }
};