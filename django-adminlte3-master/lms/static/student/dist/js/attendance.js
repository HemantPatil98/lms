(function() {
    d = new Date();
	date = d.getDate();
	// console.log(date.toString().length==1);
	// if(date.toString().length==1){
	// 	date="0"+date;
	// }
	month = d.getMonth()+1;
	// console.log(month.toString().length);
	// if(month.toString().length==1){
	// 	month="0"+month;
	// 	// month=parseInt(month, 10)
	// }
	year = d.getFullYear();
	// console.log(date,month,year);
	const currentdate = date+'/'+month+'/'+year;
	// currentdate.replaceAll('"','')
console.log(currentdate);
    var db = {

        loadData: function(filter) {
                    // console.log(filter['EMAIL ID']);
                    // addaction();
            return $.grep(this.data, function(client) {
                // console.log(!filter.name || client.name.indexOf(filter.name)>-1);
                return (!filter.ID || client.ID.indexOf(filter.ID) > -1)
                && (!filter.NAME || client.NAME.indexOf(filter.NAME) > -1)
                && (!filter.CONTACT || client.CONTACT.indexOf(filter.CONTACT) > -1)
                && (!filter['EMAIL ID'] || client['EMAIL ID'].indexOf(filter['EMAIL ID']) > -1)
                
// addaction();
            });
            // addaction();
        },

        // insertItem: function(insertingClient) {
        //     this.clients.push(insertingClient);
        // },

        // updateItem: function(rowIndex) { 
        //     // console.log(updatingRow);
        //     // alert(1);
        //     // const col = Object.keys(db.data[0]);
        //     console.log(col.length-1);
        //     len = (Object.keys(window.db.data[0]).length-1).toString();
        //     console.log(len);
        //     Url = "";
        //     if(!db.data[0][currentdate]){
        //         Url = 'window.location.origin/setdata/attendance/?rowv='+rowIndex+'&row='+len;

        //     }else{
        //         console.log("update");
        //     }
        //     // console.log(Url);
        //     data={
        //         // row:updatingRow,
        //     }
        //     // $('.btn').click(function(){
        //         $.get(Url,function(data,status){
        //             console.log(data);
        //         });
        //     // });
        // },

        // deleteItem: function(deletingClient) {
        //     var clientIndex = $.inArray(deletingClient, this.clients);
        //     this.clients.splice(clientIndex, 1);
        // }

    };


// window.db = db;
// load();
// function load(){
//     var sheetname=$("select[name='group']").val();
// console.log(sheetname);
// var url = "window.location.origin/getdata/attendance/?sheetname="+sheetname;
// $.get(url,function(data,status){
//     // console.log(data);
//     // console.log(JSON.parse(data.replaceAll("'",'"')));
//     data = data.replaceAll("'",'"');
//     db.data=JSON.parse(data);

//     fields= [
//         { name: "ID", type: "number", width: 70, css:"",editing:false},
//         { name: "NAME", type: "text", width: 150,css:"fix-name",editing:false},
//         { name: "CONTACT", type: "text", width: 100,css:'fix-contact',editing:false},
//         { name: "EMAIL ID", type: "text",width: 100,editing:false},
//         { name: "Today", type:"checkbox", width:50,editing: false}
//     ];


//     window.col = Object.keys(db.data[0]);
//     // console.log(col);
//     // fields.push({name:col[i],type:'checkbox',editing:true});
//     for(i=col.length-1;i>3;i--){
//         // console.log(col[i]);
//         if (col[i]===currentdate) {
//         fields.push({name:col[i],type:'checkbox',editing:false});

//         }
//         else{
//         fields.push({name:col[i],type:'checkbox',editing:false});

//         }
//         // console.log(fields);
//     };
//     $('#grid').jsGrid({fields:fields});
 
//     $('#grid').jsGrid({data:db.data});

//     add();

//     // $('#grid tr td:nth-child(5)').html("<input name='present' type='checkbox'></html>");
// });
// }

    


    // c = $('#data').text().replaceAll("'",'"');
 // console.log(JSON.parse(c));
    // db.data = JSON.parse(c);
    function addaction(){
      $('.jsgrid-filter-row').children('td').each(function(){
            $(this).children('input').attr('onkeypress','filter()');
          });
        $('.jsgrid-table tbody tr').click(function(){
            $('.jsgrid-edit-row').attr('onkeypress','editing(this)');
          });
        // console.log($('.jsgrid-row:nth-child(4)'));
        $('.jsgrid-table tbody tr').each(function(){
        	a=$(this)[0];
        	b=a.children[4];
        	// b.setAttribute('onclick','addattendance(this)');
        	// console.log(b);
   

        	if (db.data[0][currentdate]=="" ||db.data[0][currentdate]=="p") {
	        	e=$('.jsgrid-grid-header .jsgrid-table tr')[0].children[4];
	        	f=$('.jsgrid-grid-header .jsgrid-table tr')[1].children[4];
	        	b.setAttribute("class","hide");
	        	e.setAttribute("class","hide");
	        	f.setAttribute("class","hide");
	        	f=$('.jsgrid-grid-header .jsgrid-table tr')[0].children[5];
	        	g=a.children[5];
	        	f.innerText='Today';
	    		if(db.data[this.rowIndex][currentdate]==='p'){

	        		g.innerHTML='<input type=checkbox checked onchange=addattendance('+this.rowIndex+')></input>';
	        		present.push(this.rowIndex);
	        	}
	        	else{
	        		g.innerHTML='<input type=checkbox onchange=addattendance('+this.rowIndex+')></input>';
	        	// b.attr("class",'hide');

	        	}
        	}
        	else{
        		b.innerHTML='<input type=checkbox onchange=addattendance('+this.rowIndex+')></input>';
        	}
        		// b.innerHTML='<input type=checkbox onchange=addattendance('+this.rowIndex+')></input>';
        	
        });
    }
db.trainingmode = [
        { Name: "Offline", Id: 'Offline' },
        { Name: "Online", Id: 'Online' }
    ];
}());
        function editing(x){
        	rowIndex = x.rowIndex
          var keycode = (event.keyCode ? event.keyCode : event.which);
          if(keycode == '13'){
              edit_row = [];
              $('.jsgrid-edit-row').children('td').each(function(){
                edit_row.push($(this).children('input').val())
              });
              db.updateItem(rowIndex,edit_row);
            }
        }
          function filter(){
            var keycode = (event.keyCode ? event.keyCode : event.which);
              if(keycode == '13'){
                // console.log(typeof($('#jsGrid1').jsGrid("getFilter").name));
                a=db.loadData($('#grid').jsGrid("getFilter"));
                $('#grid').jsGrid({data:a});

              }
              // addaction();
              $('.jsgrid-filter-row').children('td').each(function(){
                $(this).children('input').attr('onkeypress','filter()');
              })
              $('.jsgrid-table tbody tr').click(function(){
                $('.jsgrid-edit-row').attr('onkeypress','editing()');
              });
          }
          // $('td').click(function(){
          //   addaction()''
          // })