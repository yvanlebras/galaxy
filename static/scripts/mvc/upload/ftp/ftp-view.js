define(["utils/utils","mvc/ui/ui-select","mvc/ui/ui-misc","mvc/upload/upload-model","mvc/upload/upload-ftp","mvc/upload/upload-extension","utils/uploadbox"],function(a,b,c,d,e,f){return Backbone.View.extend({collection:new d.Collection,initialize:function(d){var g=this;this.app=d,this.options=d.options,this.list_extensions=d.list_extensions,this.list_genomes=d.list_genomes,this.ftp_upload_site=d.currentFtp(),this.setElement(this._template()),this.ftp_list=new e({css:"upload-ftp-full",collection:this.collection,ftp_upload_site:this.ftp_upload_site,onadd:function(b){g.collection.add({id:a.uid(),mode:"ftp",name:b.path,path:b.path,file_mode:"ftp",file_name:b.path,file_size:b.size,file_path:b.path,enabled:!0})},onremove:function(a){g.collection.remove(a)}}),this.$(".upload-box").append(this.ftp_list.$el),this.btnStart=new c.Button({id:"btn-start",title:"Start",onclick:function(){g._eventStart()}}),this.btnClose=new c.Button({id:"btn-close",title:"Close",onclick:function(){g.app.modal.hide()}}),_.each([this.btnStart,this.btnClose],function(a){g.$(".upload-buttons").prepend(a.$el)}),this.select_extension=new b.View({css:"upload-footer-selection",container:this.$(".upload-footer-extension"),data:_.filter(this.list_extensions,function(a){return!a.composite_files}),value:this.options.default_extension,onchange:function(a){g.model.set("extension",a)}}),this.select_genome=new b.View({css:"upload-footer-selection",container:this.$(".upload-footer-genome"),data:this.list_genomes,value:this.options.default_genome,onchange:function(a){g.model.set("genome",a)}}),this.$(".upload-footer-extension-info").on("click",function(a){new f({$el:$(a.target),title:g.select_extension.text(),extension:g.select_extension.value(),list:g.list_extensions,placement:"top"})}).on("mousedown",function(a){a.preventDefault()}),this.listenTo(this.collection,"add remove",this.render,this),this.render()},_eventStart:function(){var a=this;this.collection.each(function(b){b.set({genome:a.select_genome.value(),extension:a.select_extension.value()})}),$.uploadpost({url:this.app.options.nginx_upload_path,data:this.app.toData(this.collection.filter()),success:function(b){a._eventSuccess(b)},error:function(a){window.console.log(a)}})},_eventSuccess:function(){Galaxy.currHistoryPanel.refreshContents()},render:function(){this.collection.length>0?(this.btnStart.enable(),this.btnStart.$el.addClass("btn-primary")):(this.btnStart.disable(),this.btnStart.$el.removeClass("btn-primary"))},_template:function(){return'<div class="upload-view-default"><div class="upload-top"><h6 class="upload-top-info"/></div><div class="upload-box upload-box-solid"/><div class="upload-footer"><span class="upload-footer-title">Type (for all):</span><span class="upload-footer-extension"/><span class="upload-footer-extension-info upload-icon-button fa fa-search"/> <span class="upload-footer-title">Genome (for all):</span><span class="upload-footer-genome"/></div><div class="upload-buttons"/></div>'}})});
//# sourceMappingURL=../../../../maps/mvc/upload/ftp/ftp-view.js.map