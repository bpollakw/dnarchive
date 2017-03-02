function vote(vote){
	if (typeof request != "undefined") {
	}else{
		request = new XMLHttpRequest();
		request.open("GET", "/" + "vote?dbid="+dbid+"&vote="+vote, true);
		request.onreadystatechange = function()
			{
				if (request.readyState == 4)
				{
					if (request.status != 200)
					{
						//error handling code here
					}
					else
					{
						response = request.responseText
						console.log(response)
					}
				}
			}

	request.send();
	}
}