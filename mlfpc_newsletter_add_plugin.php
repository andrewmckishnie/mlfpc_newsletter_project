<?php
/**
* Plugin Name: MLFPC Newsletter Add Plugin
* Plugin URI: https://www.mlfpc.ca/
* Description: This plugin is for the MLFCP Newsletter Program
* Version: 1.0
* Author: Andrew McKishnie
**/

add_action ('loop_end' , 'displayNewsletters', 1);

function addNewsletters(){
  


// Adding page
if (is_page('newsletter_db_add')){

  global $wpdb;

  $newsletter= $_GET;
  $key = $newsletter["mlfpc_key"];

  if ($key !== ""){
    die ("Something went wrong");
  }

  $url = $newsletter["URL"];
  $url = str_replace('AMPERSAND', '&', $url);
  var_dump($url);

  $url_check_query = "SELECT newsletter_id FROM newsletters WHERE newsletter_url = %s ";
  $url_check = $wpdb -> query(
  $wpdb -> prepare($url_check_query, array($url))
  ) ;


  if ($url_check == NULL) {

    $topics = $wpdb -> get_results('SELECT * FROM newsletter_topics') ;
    $topics_array_name_keys = array();
    foreach($topics as $topic){
      $top_ref_id = $topic -> topic_id;
      $topic_name = $topic -> topic_name;
      $topics_array_name_keys[$topic_name] = (int)$top_ref_id ;
    }

  $dat = $newsletter["Date"];
  $top_1_id = $topics_array_name_keys[$newsletter["Topic_1"]];
  $top_2_id = $topics_array_name_keys[$newsletter["Topic_2"]];
  $top_3_id = $topics_array_name_keys[$newsletter["Topic_3"]];
  $top_4_id = $topics_array_name_keys[$newsletter["Topic_4"]];
  $top_5_id = $topics_array_name_keys[$newsletter["Topic_5"]];
  $src_name = $newsletter["Source"];

  $source_id_query = "SELECT source_id FROM newsletter_sources WHERE source_name = %s ";
  $src_id = $wpdb -> get_var(
    $wpdb -> prepare($source_id_query, array($src_name))
  );
  $src_id = (int)$src_id;

  if ($src_id == NULL){
    $wpdb -> query(
      $wpdb -> prepare(
      'INSERT INTO newsletter_sources (source_name) VALUE (%s)', array($src_name)
        )
      );
      $src_id = $wpdb -> insert_id;

  }

  $new_newsletter_query = "INSERT INTO newsletters
    (newsletter_url, newsletter_date, source_id, topic_1_id, topic_2_id, topic_3_id, topic_4_id, topic_5_id)
    VALUES (%s, %s, %d, %d, %d, %d, %d, %d)"   ;
  $new_newsletter_info = array($url, $dat, $src_id, $top_1_id, $top_2_id, $top_3_id, $top_4_id, $top_5_id);
  $wpdb -> query(
    $wpdb -> prepare($new_newsletter_query, $new_newsletter_info)
    )   ;

  }










}
}

?>
