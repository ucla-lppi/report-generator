document.addEventListener('DOMContentLoaded', function () {
    const countyName = "{{ county_name }}"; // This should be dynamically set based on the context

    Papa.parse('https://docs.google.com/spreadsheets/d/e/2PACX-1vTDl0u8xAvazJjlCn62edUDjjK1tLwyi4hXihYpYIGOxawrN3_HfzvYKJ1ARzH4AzhrHZysIpkc_1Nc/pub?output=csv', {
        download: true,
        header: true,
        complete: function (results) {
            const data = results.data;
            const countyData = data.find(row => row.county_name === countyName);

            if (countyData) {
                document.getElementById('total-pop').textContent = countyData.pop;
                document.getElementById('latino-pop').textContent = countyData.latino;
                document.getElementById('nlw-pop').textContent = countyData.nlw;
            } else {
                console.error('County data not found');
            }
        },
        error: function (error) {
            console.error('Error fetching data:', error);
        }
    });
});