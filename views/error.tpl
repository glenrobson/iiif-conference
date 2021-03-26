<!DOCTYPE html>

% from model.config import Config
% conf = Config()
<html>
<head>
	<title>Error Page</title>
   
	<!--Bootsrap 4 CDN-->
	<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
    
    <!--Fontawesome CDN-->
	<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.3.1/css/all.css" integrity="sha384-mzrmE5qonljUremFsqc01SB46JvROS7bZs3IO2EmfFsd15uHvIt+Y8vEf7N7fWAU" crossorigin="anonymous">

	<!--Custom styles-->
	<link rel="stylesheet" type="text/css" href="static/css/login.css">
</head>
<body style="background-image: url('{{ conf.website('hero_image') }}');">
<div class="container">
	<div class="d-flex justify-content-center h-100">
		<div class="card">
			<div class="card-header">
				<h2>{{error_title}}</h2><div class="float-right"><img src="https://i0.wp.com/www.clir.org/wp-content/uploads/sites/6/2016/09/IIIF-logo-500w.png?w=500&ssl=1" height="50px"/></div>
			</div>
			<div class="card-body" style="background-color: azure;">
                {{!error_body}}
            </div>
			<div class="card-footer">
				<div class="d-flex justify-content-center links">
                    {{ conf.website('title') }}
				</div>
			</div>
		</div>
	</div>
</div>
</body>
</html>
