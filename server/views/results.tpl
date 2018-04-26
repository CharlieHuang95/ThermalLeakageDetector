<!DOCTYPE html>
<html lang="en">
<head><title>Results</title>
    <style>
        h1 {color: #20B2AA; text-align: center; padding-top: 120px; font-family: "Lucida Sans Unicode", "Lucida Grande", sans-serif;}
        h2 {text-align: center;}
        h3 {text-align: center;}
        p {text-align: center; margin: 0 auto; width:40%;}
        img {display: block; margin-left: auto; margin-right: auto; max-height: 500px; height: 90%; width: auto;}
        #resultsTable {margin: auto;}
    </style>
</head>
<body>
        <div><img src="{{link}}">
        <h3>Leakage Description</h3>
        <p>{{description}}</p>
        <div id="results">
            <table id="resultsTable">
                <tr><th>Recommendations for {{leakage}}</th></tr>
                %for i in range(len(recommendations)):
                    %rec = recommendations[i]
                    %rec_divided = "+".join(rec.split())
                    <tr><td><a href="https://www.amazon.com/s?url=search-alias%3Daps&field-keywords={{rec_divided}}">{{rec}}</a></td></tr>
                %end
            </table>
        </div>
        <h3>See more energy saving tips at <a href="{{infosite}}">energy.gov</a>!</h3>
</body>
</html>