const axios = require("axios");
const cheerio = require("cheerio");

(async () => {
  const url = "https://www.rentmystay.com/Info/faq";
  const { data: html } = await axios.get(url);

  const $ = cheerio.load(html);

  const faqs = [];
  // The pattern: headings start with '##  ' indicating questions
  $('body').children().each((_, elem) => {
    const text = $(elem).text().trim();
    if (text.startsWith("##")) {
      const question = text.replace(/^##\s*/, "").trim();
      let answer = "";

      // Collect answer lines until next question heading
      let next = $(elem).next();
      while (next.length && !next.text().trim().startsWith("##")) {
        answer += next.text().trim() + " ";
        next = next.next();
      }

      faqs.push({ question, answer: answer.trim() });
    }
  });

  console.log(faqs);
})();
