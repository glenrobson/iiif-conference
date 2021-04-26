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
<nav class="navbar navbar-expand-md navbar-dark bg-dark btco-hover-menu">
    <a class="navbar-brand" href="https://iiif.io"><img src="https://i0.wp.com/www.clir.org/wp-content/uploads/sites/6/2016/09/IIIF-logo-500w.png?w=500&ssl=1" height="30px"/></a>
    <a class="navbar-brand" href="/index.html">{{ conf.website('title') }}</a>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarCollapse" aria-controls="navbarCollapse" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
    </button>
    % if defined('role') and role == 'admin':
        <div class="navbar-collapse collapse w-100 order-2 dual-collapse2">
            <ul class="navbar-nav m1-auto">
                <li class="nav-item">
                    <a class="nav-link" href="/admin.html">Admin</a>
                </li>
            </ul>    
        </div>
    % end 
    <div class="navbar-collapse collapse w-100 order-3 dual-collapse2">
        <ul class="navbar-nav m1-auto" style="right: 20px; position: absolute;">
            <li class="nav-item">
                <a class="nav-link" href="/logout">Logout</a>
            </li>
        </ul>    
    </div>
</nav>
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
