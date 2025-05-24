const nodemailer = require('nodemailer');
const config = require('../config/config');

const sendEmail = async options => {
  // Create a transporter
  const transporter = nodemailer.createTransport({
    host: config.smtpHost,
    port: config.smtpPort,
    auth: {
      user: config.smtpUser,
      pass: config.smtpPass
    }
  });

  // Define email options
  const mailOptions = {
    from: `FitGent <${config.emailFrom}>`,
    to: options.email,
    subject: options.subject,
    text: options.message,
    html: options.html
  };

  // Send email
  await transporter.sendMail(mailOptions);
};

module.exports = sendEmail;
